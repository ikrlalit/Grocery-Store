import os
from datetime import datetime
from flask_restful import Resource,fields, marshal_with, reqparse, request
from flask import current_app as app
from application.models import Category, Product, Cart, User
from application.database import *
from application.validation import NotFoundError, BusinessValidationError, NotAuthorizedError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required,get_jwt_identity


def get_user_role():
    current_user=get_jwt_identity()
    user=User.query.filter_by(username=current_user).first()
    return user.role

#--------------------------USER APIs---------------------------------

create_user_parser=reqparse.RequestParser()
create_user_parser.add_argument("username")
create_user_parser.add_argument("password")
create_user_parser.add_argument("role")

create_user_login_parser=reqparse.RequestParser()
create_user_login_parser.add_argument("username")
create_user_login_parser.add_argument("password")

class UserLogin(Resource):
    def post(self):
        args=create_user_login_parser.parse_args()
        username=args.get("username",None)
        password=args.get("password",None)
        user = User.query.filter_by(username=username).first()
        if user:
            hashed_password=user.password
            is_valid_password=check_password_hash(hashed_password,password)
            if is_valid_password:
                access_token = create_access_token(identity=user.username)
                return {'access_token': access_token},200
            else:
                return "Authentication failed! Invalid password.", 401
        else:
            return "User not found!", 401
class UserSignup(Resource):        
    def post(self):
        args=create_user_parser.parse_args()
        username=args.get("username",None)
        password=args.get("password",None)
        role=args.get("role",None)
        if not username or username.strip() == "":
            raise BusinessValidationError(400,"UBE001","Username is required")
        user_name=User.query.filter_by(username=username).first()
        if user_name:
            raise BusinessValidationError(400,"UBE002","User already exist")
        if not password or password.strip() == "":
            raise BusinessValidationError(400,"UBE003","Invalid password. Whitespace are not allowed.")
        if not role or username.strip() == "":
            raise BusinessValidationError(400,"UBE004","Role is required")
        if role not in ["admin","user"]:
            raise BusinessValidationError(400,"UBE005","Invalid role type")
        
        hashed_password = generate_password_hash(password)
        try:
            user=User(username=username, password=hashed_password,role=role)
            db.session.add(user)
            db.session.commit()
            return "User account created successfully", 201
        except Exception as e:
            return {"Error",str(e)},500
        
#=================================== CATEGORY APIs================================

category_fields={
    "category_id":fields.Integer,
    "category_name": fields.String   
}

create_category_parser=reqparse.RequestParser()
create_category_parser.add_argument("category_name")

update_category_parser=reqparse.RequestParser()
update_category_parser.add_argument("category_name")



class CategoryAPI(Resource):
    @marshal_with(category_fields)
    def get(self,category_id):
        category=Category.query.filter_by(category_id=category_id).first()
        if category:
            return category,200
        else:
            raise NotFoundError(status_code="404")
        
    @marshal_with(category_fields)
    @jwt_required()    
    def put(self,category_id):
        if get_user_role()=="admin":
            args=update_category_parser.parse_args()
            category_name=args.get("category_name",None)
            category = Category.query.filter_by(category_id=category_id).first()
            if category_name is None or category_name.strip() == "":
                raise BusinessValidationError(status_code=400, error_code="CBE001", error_message="Category_name is required")
            if category is None:
                raise NotFoundError(status_code=404)
            category.category_name=category_name
            db.session.commit()
            return category,200
        else:
            raise NotAuthorizedError(status_code=403, error_message="Access Denied")

    @jwt_required() 
    def delete(self,category_id):
        if get_user_role()=="admin":        
            category = Category.query.filter_by(category_id=category_id).first()
            if category is not None:
                products= Product.query.filter_by(category_id=category_id).all()
                for product in products:
                    products_in_cart=Cart.query.filter_by(product_id=product.product_id).all()
                    if products_in_cart:
                        for cart_product in products_in_cart:
                            db.session.delete(cart_product)
                        db.session.commit()
                    db.session.delete(product)
                db.session.delete(category)
                db.session.commit()
                return "Category deleted Successfully",200
            else:
                return "Category not found",404
        else:
            raise NotAuthorizedError(status_code=403, error_message="Access Denied")
    
    @marshal_with(category_fields)
    @jwt_required() 
    def post(self):
        if get_user_role()=="admin":        
            args=create_category_parser.parse_args()
            category_name=args.get("category_name",None)
            if not category_name or category_name.strip() == "":
                raise BusinessValidationError(400,"CBE001","Category name is required")
            check_category=Category.query.filter_by(category_name=category_name).first()
            if check_category:
                raise BusinessValidationError(status_code=400,error_code="CBE002",error_message="Category already exist!")
            try: 
                new_category=Category(category_name=category_name)
                db.session.add(new_category)
                db.session.commit()
                return new_category, 201
            except Exception as e:
                return {"error": str(e)},500
        else:
            raise NotAuthorizedError(status_code=403, error_message="Access Denied")
        
###=================================== Product APIs==================================   
 
product_fields={
    "product_name": fields.String,
    "product_description":fields.String,
    "unit":fields.String,
    "price":fields.Integer,
    "quantity":fields.Integer,
    "mfg_date":fields.String,
    "expiry_date":fields.String,
    "product_image":fields.String,
    "category_id":fields.Integer
}

update_product_parser=reqparse.RequestParser()
update_product_parser.add_argument("category_name")

    
class ProductAPI(Resource):
    @marshal_with(product_fields)
    def get(self,product_id):
        product=Product.query.filter_by(product_id=product_id).first()
        if product:
            return product, 200
        else:
            raise NotFoundError(status_code="404")
    
    @marshal_with(product_fields)  
    @jwt_required()  
    def put(self,product_id):
        if get_user_role()=="admin":         
            product=Product.query.filter_by(product_id=product_id).first()
            if product:
                if "product_name" not in request.form or request.form["product_name"].strip() == "":
                    raise BusinessValidationError(status_code=400, error_code="PBE001", error_message="Product name is required")
                if "product_description" not in request.form or request.form["product_description"].strip() == "":
                    raise BusinessValidationError(status_code=400, error_code="PBE003", error_message="Product description is required")
                if "unit" not in request.form or request.form["unit"].strip() == "":
                    raise BusinessValidationError(status_code=400, error_code="PBE004", error_message="Unit is required")
                if "price" not in request.form or request.form["price"].strip() == "":
                    raise BusinessValidationError(status_code=400, error_code="PBE005", error_message="price is required")
                if "quantity" not in request.form or request.form["quantity"].strip() == "":
                    raise BusinessValidationError(status_code=400, error_code="PBE006", error_message="Product quantity is required")
                if "mfg_date" not in request.form or request.form["mfg_date"].strip() == "":
                    raise BusinessValidationError(status_code=400, error_code="PBE007", error_message= "Manufacturing date is required")
                if "expiry_date" not in request.form or request.form["expiry_date"].strip() == "":
                    raise BusinessValidationError(status_code=400, error_code="PBE008", error_message="Expiry date is required")
                if "product_image" not in request.files:
                    raise BusinessValidationError(status_code=400, error_code="PBE009", error_message="Image is required")
                try:    
                    product.product_name= request.form["product_name"]
                    product.product_description= request.form["product_description"]
                    product.unit= request.form["unit"]
                    product.price= request.form["price"]
                    product.quantity= request.form["quantity"]
                    mfg_date_str=request.form["mfg_date"]
                    product.mfg_date= datetime.strptime(mfg_date_str, '%Y-%m-%d').date()
                    expiry_date_str=request.form["expiry_date"]
                    product.expiry_date= datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
                    img_file=request.files['product_image']
                    filename=img_file.filename
                    product.product_image=filename
                    img_file.save(os.path.join(app.config['UPLOAD_FOLDER']+ filename))
                    db.session.commit()
                    return product, 200
                except Exception as e:
                    return {"error":str(e)},500
            else:
                raise NotFoundError(status_code=404)
        else:
            raise NotAuthorizedError(status_code=403, error_message="Access Denied")
        
    @jwt_required()
    def delete(self,product_id):
        if get_user_role()=="admin":          
            product = Product.query.filter_by(product_id=product_id).first()
            if product:  
                products_in_cart=Cart.query.filter_by(product_id=product_id).all()
                if products_in_cart:
                    for cart_product in products_in_cart:
                        db.session.delete(cart_product)
                    db.session.commit()
                db.session.delete(product)
                db.session.commit()
                return "Product deleted successfully", 200
            else:
                raise NotFoundError(status_code=404)
        else:
            raise NotAuthorizedError(status_code=403, error_message="Access Denied")
    
 
    @marshal_with(product_fields)
    @jwt_required()
    def post(self,category_id):
        if get_user_role()=="admin":          
            category=Category.query.filter_by(category_id=category_id).first()
            if category:
                if "product_name" not in request.form or request.form["product_name"].strip() == "":
                    raise BusinessValidationError(status_code=400, error_code="PBE001", error_message="Product name is required")
                prod_name=request.form["product_name"]
                product=Product.query.filter_by(product_name=prod_name).first()
                if product:
                    raise BusinessValidationError(status_code=400, error_code="PBE002", error_message="Product already exist.")
                if "product_description" not in request.form or request.form["product_description"].strip() == "":
                    raise BusinessValidationError(status_code=400, error_code="PBE003", error_message="Product description is required")
                if "unit" not in request.form or request.form["unit"].strip() == "":
                    raise BusinessValidationError(status_code=400, error_code="PBE004", error_message="Unit is required")
                if "price" not in request.form or request.form["price"].strip() == "":
                    raise BusinessValidationError(status_code=400, error_code="PBE005", error_message="price is required")
                if "quantity" not in request.form or request.form["quantity"].strip() == "":
                    raise BusinessValidationError(status_code=400, error_code="PBE006", error_message="Product quantity is required")
                if "mfg_date" not in request.form or request.form["mfg_date"].strip() == "":
                    raise BusinessValidationError(status_code=400, error_code="PBE007", error_message= "Manufacturing date is required")
                if "expiry_date" not in request.form or request.form["expiry_date"].strip() == "":
                    raise BusinessValidationError(status_code=400, error_code="PBE008", error_message="Expiry date is required")
                if "product_image" not in request.files:
                    raise BusinessValidationError(status_code=400, error_code="PBE009", error_message="Image is required")
                try:
                    product_name = request.form['product_name']
                    product_description=request.form['product_description']
                    unit=request.form['unit']
                    price=request.form['price']
                    quantity=request.form['quantity']
                    mfg_date_str=request.form['mfg_date']
                    expiry_date_str=request.form['expiry_date']
                    img_file=request.files['product_image']
                    filename=img_file.filename
                    mfg_date = datetime.strptime(mfg_date_str, '%Y-%m-%d').date()
                    expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
                    product=Product(product_name=product_name,product_description=product_description,unit=unit,price=price, quantity=quantity,mfg_date=mfg_date,expiry_date=expiry_date,product_image=filename,category_id=category_id)
                    img_file.save(os.path.join(app.config['UPLOAD_FOLDER']+ filename))
                    db.session.add(product)
                    db.session.commit()
                    return product, 201
                except Exception as e:
                    return {"error": str(e)}, 500
            else:
                raise NotFoundError(status_code=400)
        else:
            raise NotAuthorizedError(status_code=403, error_message="Access Denied")
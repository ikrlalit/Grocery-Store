import os
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import redirect,request,render_template,url_for
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from application.models import *
from application.config import *
from application.database import db


login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
       return User.query.get(int(id))

@app.route('/')
def home():
    return render_template('home.html')

@ app.route("/user_signup", methods=['GET','POST'])
def user_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role=request.form['role']
        
        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            flag=0
            return render_template("signup.html",flag=flag)
        
        if username and password:
            hashed_password = generate_password_hash(password)
            user = User(username=username, password=hashed_password,role=role)
            db.session.add(user)
            db.session.commit()
            flag=1
            return render_template('user_login.html', flag=flag)
        else:
            flag=2
            return render_template('signup.html',flag=flag)
    
    return render_template("signup.html")

@ app.route("/admin_signup", methods=['GET','POST'])
def admin_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role=request.form['role']
        
        
        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            flag=0
            return render_template("admin_signup.html",flag=flag)
        
        if username and password:
            hashed_password = generate_password_hash(password)
            user = User(username=username, password=hashed_password,role=role)
            db.session.add(user)
            db.session.commit()
            flag=1
            return render_template('user_login.html', flag=flag)
        else:
            flag=2
            return render_template('admin_signup.html',flag=flag)
    
    return render_template("admin_signup.html")

@ app.route("/user_login", methods=['GET','POST'])
def  user_login():
    if request.method=="POST":
        username=request.form['username']
        password=request.form['password'] 
        user=User.query.filter_by(username=username).first()
        if user is None:
            flag=2
            return render_template("user_login.html",flag=flag)
        else:
            hashed_password=user.password
            is_valid_password=check_password_hash(hashed_password,password)
            if user and is_valid_password:
                login_user(user)
                if user.role=='admin':
                    return redirect(url_for('admin_dashboard'))
                elif user.role=='user':
                    return redirect(url_for('user_dashboard'))
            else:
                flag=0
                return render_template('user_login.html',flag=flag)
    else:
        return render_template("user_login.html")

@ app.route("/user_dashboard")
@login_required
def user_dashboard():
    products=Product.query.all()
    products.reverse()
    categories = Category.query.all()
    category_count=len(categories)
    product_count=len(products)
    user_id=current_user.get_id()
    cart_items=Cart.query.filter_by(user_id=user_id).all()
    total_cart_items=len(cart_items)
    user=User.query.filter_by(user_id=user_id).first()
    user_name=user.username
    print(user_name)


    return render_template("user_dashboard.html",products=products,product_count=product_count,total_cart_items=total_cart_items, category_count=category_count,categories=categories,user_name=user_name)

@app.route("/admin_dashboard")
@login_required 
def admin_dashboard():
    category_count = db.session.query(Category).count()
    categories = Category.query.all()
    admin_name=current_user.username
    if current_user.role=='admin':
        return render_template("admin_dashboard.html",category_count=category_count,categories=categories,admin_name=admin_name)
    else:
        return render_template("403.html")
#============ CRUD for Category ====================

@app.route("/add_category", methods=['GET','POST'])
@login_required
def add_category():
    if current_user.role=='admin':
        if request.method=='POST':
            category_name=request.form['category_name']
            category=Category.query.filter_by(category_name=category_name).first()
            if category:
                return render_template('add_category.html',flag=0)
            if not category_name or category_name.strip() == "":
                return render_template('add_category.html',flag=1)
            category=Category(category_name=category_name)
            db.session.add(category)
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('add_category.html')
    else:
        return render_template('403.html')
    
@app.route('/category/<int:category_id>/add_product',methods=['GET','POST'])
def add_product(category_id):
    if current_user.role=='admin':
        if request.method=='POST':
            product_name=request.form['product_name']
            if not product_name or product_name.strip() == "":
                return render_template("add_product.html",category_id=category_id, flag=0 )
            product=Product.query.filter_by(product_name=product_name).first()
            if product:
                return render_template("add_product.html",category_id=category_id, flag=1 )
            product_description=request.form['product_desc']
            if not product_description or product_description.strip() == "":
                return render_template("add_product.html",category_id=category_id, flag=2 )
            unit=request.form['unit']
            price=request.form['price']
            total_quantity=request.form['quantity']
            mfg_date_str=request.form['mfg_date']
            expiry_date_str=request.form['expiry_date']
            img_file=request.files['product_image']
            filename=img_file.filename
            mfg_date = datetime.strptime(mfg_date_str, '%Y-%m-%d').date()
            expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
            product=Product(product_name=product_name,product_description=product_description,unit=unit,price=price, quantity=total_quantity,category_id=category_id,mfg_date=mfg_date,expiry_date=expiry_date,product_image=filename)
            img_file.save(os.path.join(app.config['UPLOAD_FOLDER']+ filename))
            db.session.add(product)
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('add_product.html',category_id=category_id)
    else:
        return render_template('403.html')

@app.route('/category/<int:category_id>/update', methods=['GET','POST'])
def update_category(category_id):
    if current_user.role=='admin':
        category = Category.query.get(category_id)
        if request.method=='POST':
            category = Category.query.filter_by(category_id=category_id).first()
            updated_category_name = request.form['category_name']
            if not updated_category_name or updated_category_name.strip() == "":
                return render_template('update_category.html',category=category,flag=0)
            category.category_name=updated_category_name
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('update_category.html',category=category)
    else:
        return render_template('403.html')

@app.route('/category/<int:category_id>/delete')
def delete_category(category_id):
    if current_user.role=='admin':
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
            return redirect(url_for('admin_dashboard'))
    else:
        return render_template('403.html')

#=================== CRUD for Products ====================

@app.route('/category/<int:category_id>/show_product')
def show_product(category_id):
    if current_user.role=='admin':
        products = Product.query.filter_by(category_id=category_id).all()
        category= Category.query.filter_by(category_id=category_id).first()
        category_name=category.category_name
        product_count= len(products)
        return render_template('show_product_list.html',products=products,product_count=product_count,category_id=category_id, category_name=category_name)
    else:
        return render_template('403.html')
@app.route('/product/<int:product_id>/update', methods=['GET','POST'])
def update_product(product_id):
    if current_user.role=='admin':
        product = Product.query.filter_by(product_id=product_id).first()
        if request.method=='POST':
            category_id=product.category_id
            product_name= request.form['product_name']
            if not product_name or product_name.strip() == "":
                return render_template("update_product.html",product=product, flag=0 )
            product.product_name=product_name
            product_desc=request.form['product_desc']
            if not product_desc or product_desc.strip() == "":
                return render_template("update_product.html",product=product, flag=1 )
            product.product_description=product_desc
            product.unit=request.form['unit']
            product.price=request.form['price']
            product.quantity=request.form['quantity']
            mfg_date_str=request.form["mfg_date"]
            product.mfg_date= datetime.strptime(mfg_date_str, '%Y-%m-%d').date()
            expiry_date_str=request.form["expiry_date"]
            product.expiry_date= datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
            img_file=request.files['product_image']
            filename=img_file.filename
            product.product_image=filename
            img_file.save(os.path.join(app.config['UPLOAD_FOLDER']+ filename))
            db.session.commit()
            return redirect(url_for('show_product',category_id=category_id))
        else:
            return render_template('update_product.html',product=product)
    else:
        return render_template('403.html')
@app.route('/product/<int:product_id>/delete')
def delete_product(product_id):
    if current_user.role=='admin':
        product = Product.query.filter_by(product_id=product_id).first()
        products_in_cart=Cart.query.filter_by(product_id=product_id).all()
        if products_in_cart:
            for cart_product in products_in_cart:
                db.session.delete(cart_product)
            db.session.commit()
        if product is not None:
            category_id=product.category_id
            db.session.delete(product)
            db.session.commit()
            return redirect(url_for('show_product',category_id=category_id))
    else:
        return render_template('403.html')

@app.route("/<path:category_name>")
def category_wise_products(category_name):
    category=Category.query.filter_by(category_name=category_name).first()
    products=[]
    product_count=0
    if category is not None:
        category_id=category.category_id
        products=Product.query.filter_by(category_id=category_id).all()
        products.reverse()
        product_count=len(products)
    categories=Category.query.all()
    category_count=len(categories)
    user=current_user
    if user.is_authenticated:
        user_name=user.username
        cart_items = Cart.query.filter_by(user_id=current_user.user_id).all()
        total_cart_items = len(cart_items)
        return render_template('loggedin_categorywise_view.html',products=products,product_count=product_count,category_count=category_count,categories=categories,category_name=category_name,total_cart_items=total_cart_items,user_name=user_name)
    else:
        return redirect(url_for('user_login'))
@app.route('/info/<int:product_id>/')
def product_info(product_id):
    product_info = Product.query.filter_by(product_id=product_id).first()
    print(current_user)
    user = current_user
    cart_items = Cart.query.filter_by(user_id=current_user.user_id).all()
    total_cart_items = len(cart_items)
    return render_template("loggedin_product_info.html", product_info=product_info, total_cart_items=total_cart_items)


#===============  CART CONTROLLERS HERE ===========================

@app.route('/<int:product_id>/add_to_cart',methods=["GET","POST"])
def add_to_cart(product_id):
    if request.method=="POST":
        user_id=current_user.get_id()
        item_quantity=int(request.form['item_quantity'])
        product=Product.query.filter_by(product_id=product_id).first()
        if product.quantity>=item_quantity:
            cart_item=Cart.query.filter_by(user_id=user_id,product_id=product_id).first()
            if cart_item is not None:
                cart_item.item_quantity+=item_quantity
                product.quantity-=item_quantity
                db.session.commit()
            else:
                item=Cart(user_id=user_id,product_id=product_id,item_quantity=item_quantity)
                product.quantity-=item_quantity
                db.session.add(item)
                db.session.commit()
        else:
            pass
            #Out of stock
        return redirect(url_for('user_dashboard'))

@app.route('/cart')
def get_cart_data():
    products=Product.query.all()
    user_id=current_user.get_id()
    cart_items=Cart.query.filter_by(user_id=user_id).all()
    total_cart_items=len(cart_items)
    item_dict={}
    total=0
    for i in cart_items:
        for j in products:
            if i.product_id == j.product_id:
                item_dict[i.product_id]=[i.product_id,j.product_name, i.item_quantity, j.price]
                total+=(i.item_quantity*j.price)
    item_values=list(item_dict.values())
    return render_template("cart.html",item_values=item_values,total_cart_items=total_cart_items,total=total)


@app.route('/update_cart',methods=['GET','POST'])
def update_cart():
    if current_user is None:
        return redirect('user_login')
    else:
        user_id=current_user.get_id()
        product_id=request.form.get('item_id')
        cart_item=Cart.query.filter_by(user_id=user_id,product_id=product_id).first()
        product=Product.query.filter_by(product_id=product_id).first()
        action=request.form.get('action')
        print(product)
        if action=='step_up':
            if(product.quantity>0):
                product.quantity-=1
                cart_item.item_quantity+=1
                db.session.commit()
                return redirect(url_for('get_cart_data'))
            else:
                cart_item.item_quantity+=0
                # Out of stock
                return redirect(url_for("get_cart_data"))
        elif action=='step_down':
            cart_item.item_quantity-=1
            product.quantity+=1
            if cart_item.item_quantity<1:
                db.session.delete(cart_item)
                db.session.commit()
            db.session.commit()
            return redirect(url_for('get_cart_data'))

#========= Controller for Search ========

@app.route('/search',methods=['GET','POST'])
def search_result():
    if request.method=='POST':
        query= request.form['search_query']
        result= CategorySearch.query.filter(CategorySearch.category_name.op("MATCH")(query)).all()
        result1= ProductSearch.query.filter(ProductSearch.product_name.op("MATCH")(query)).all()
        result2= ProductSearch.query.filter(ProductSearch.product_description.op("MATCH")(query)).all()
        all_product_ids=[]
        all_products=[]
        for item in result:
            products=Product.query.filter_by(category_id=item.category_id).all()
            all_products+=products
            products=[]
        for id in all_products:
            all_product_ids+=[id.product_id]
        for item in result1:
            all_product_ids+=[item.product_id]
        for item in result2:
            all_product_ids+=[item.product_id]

        products_list=list(set(all_product_ids))
        result_product_list=[]
        for i in products_list:
            products=Product.query.filter_by(product_id=i).one()
            result_product_list+=[products]
        product_count=len(result_product_list)
        categories=Category.query.all()
        category_count=len(categories)
        user = current_user
        if user.is_authenticated:
            cart_items = Cart.query.filter_by(user_id=current_user.user_id).all()
            total_cart_items = len(cart_items)
            return render_template('loggedin_search_result.html',result_product_list=result_product_list,categories=categories,category_count=category_count,product_count=product_count,total_cart_items=total_cart_items)
    else:
        if user.is_authenticated:
            return redirect(url_for('user_dashboard'))
        else:
            return redirect(url_for('home'))
        
# Order Summary Admin dashboard
@app.route('/summary')
@login_required
def summary():
    user = current_user
    if user.is_authenticated:
        if user.role=='admin':
            productlist_quantitysum = (db.session.query(Cart.product_id, db.func.sum(Cart.item_quantity)).group_by(Cart.product_id).all())
            prod_name=[]
            prod_quantity=[]
            categorylist=[]
            for i in productlist_quantitysum:
                product=Product.query.filter_by(product_id=i[0]).first()
                prod_name.append(product.product_name)
                category=Category.query.filter_by(category_id=product.category_id).first()
                categorylist.append((category.category_name))
                prod_quantity.append(i[1])

            category_counts = {}
            for category in categorylist:
                if category in category_counts:
                    category_counts[category] += 1
                else:
                    category_counts[category] = 1
            print(category_counts)
            categories = list(category_counts.keys())
            counts = list(category_counts.values())
            plt.subplots(figsize=(12, 8))
            plt.bar(prod_name,prod_quantity)
            plt.xticks(rotation=45)
            plt.subplots_adjust(bottom=0.2)
            plt.xlabel("Product",fontsize=16)
            plt.ylabel("Quantity",fontsize=16)
            plt.title("Product Demand Graph",fontsize=25)

            plt.savefig('static/product_demand_graph.png')
            plt.close()

            plt.subplots(figsize=(12, 8))
            plt.bar(categories,counts)
            plt.xticks(rotation=45)
            plt.subplots_adjust(bottom=0.2)
            plt.xlabel("Category",fontsize=16)
            plt.ylabel("Quantity",fontsize=16)
            plt.title("Categorywise Product Demand Graph",fontsize=25)

            plt.savefig('static/category_demand_graph.png')
            plt.close()

            return render_template('summary.html')
        else:
            return render_template('403.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
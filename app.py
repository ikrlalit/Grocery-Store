from datetime import timedelta
from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from application.config import *
from application.database import db
from flask_jwt_extended import JWTManager

app = None
api = None

def create_app(UPLOAD_FOLDER, DB):
    app = Flask(__name__,template_folder="templates")
    CORS(app)
    app.secret_key='Soemedkjjt4ewrdcxx'
    app.config['SQLALCHEMY_DATABASE_URI'] = DB
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['JWT_SECRET_KEY'] = 'JWtSecrteKEy232'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['CORS_HEADERS']= 'Content-Type '
    db.init_app(app)
    api=Api(app)
    app.app_context().push()
    return app,api
app,api = create_app(UPLOAD_FOLDER, DB)

jwt=JWTManager(app)

from application.controllers import *
from application.api import CategoryAPI, ProductAPI, UserLogin, UserSignup
# All APIs here
api.add_resource(UserLogin,"/api/user/login")
api.add_resource(UserSignup,"/api/user" )
api.add_resource(CategoryAPI,"/api/category/<int:category_id>","/api/category")
api.add_resource(ProductAPI,"/api/product/<int:product_id>","/api/<int:category_id>/product")

if __name__=='__main__':
    create_categorysearch_table()
    create_productsearch_table()
    db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)

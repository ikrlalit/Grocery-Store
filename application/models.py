from flask_login import UserMixin
from datetime import datetime
from application.database import db
from sqlalchemy import create_engine,text, event
from sqlalchemy.orm import sessionmaker

engine=create_engine("sqlite:///app_db.sqlite3")
Session = sessionmaker(bind=engine)

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50), nullable=False)
    role=db.Column(db.String(50),nullable=False)

    def get_id(self):
        return str(self.user_id)

class Category(db.Model):
    __tablename__ = 'category'

    category_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    category_name = db.Column(db.String(150), unique=True)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    __tablename__ = 'product'

    product_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    product_name = db.Column(db.String(150), unique=True)
    product_description = db.Column(db.String(500))
    unit = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    mfg_date = db.Column(db.Date)  
    expiry_date = db.Column(db.Date)
    product_image = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'))

class Cart(db.Model):
    __tablename__ = 'cart'
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), primary_key=True)
    item_quantity = db.Column(db.Integer)
    
    user = db.relationship('User', backref=db.backref('cart_items', lazy=True))
    product = db.relationship('Product', backref=db.backref('cart_items', lazy=True))


def create_categorysearch_table():
    db.session.execute(text("""
        CREATE VIRTUAL TABLE IF NOT EXISTS category_search USING fts5(category_id, category_name, tokenize = "porter unicode61");
    """))
    db.session.commit()

def create_productsearch_table():
    db.session.execute(text("""
        CREATE VIRTUAL TABLE IF NOT EXISTS product_search USING fts5(product_id, product_name, product_description, tokenize = "porter unicode61");
    """))
    db.session.commit()


class CategorySearch(db.Model):
    __tablename__='category_search'
    category_id=db.Column(db.Integer,primary_key=True)
    category_name=db.Column(db.String(150))

class ProductSearch(db.Model):
    __tablename__='product_search'
    product_id=db.Column(db.Integer,primary_key=True)
    product_name=db.Column(db.String(150))
    product_description=db.Column(db.String(500))



### Triggers for CategorySearch

@event.listens_for(Category, 'after_insert')
def category_after_insert(mapper, connection, target):
    session = Session(bind=connection)
    session.execute(
        text("""
        INSERT INTO category_search(category_id, category_name)
        VALUES (:category_id, :category_name)
        """),
        {
            'category_id': target.category_id,
            'category_name': target.category_name
        }
    )
    session.commit()
    session.close()

@event.listens_for(Category, 'after_delete')
def category_after_delete(mapper, connection, target):
    session = Session(bind=connection)
    session.execute(text("""
        DELETE FROM category_search WHERE category_id = :category_id"""), {
        'category_id': target.category_id
    })
    session.commit()
    session.close()

@event.listens_for(Category, 'after_update')
def category_after_update(mapper, connection, target):
    session = Session(bind=connection)
    
    session.execute(text("""
        DELETE FROM category_search WHERE category_id = :category_id
    """), {'category_id': target.category_id})
    
    session.execute(text("""
        INSERT INTO category_search(category_id, category_name) VALUES (:category_id, :category_name)
    """), {'category_id': target.category_id, 'category_name': target.category_name})
    
    session.commit()
    session.close()

### Triggers for ProductSearch

@event.listens_for(Product, 'after_insert')
def product_after_insert(mapper, connection, target):
    session = Session(bind=connection)
    session.execute(
        text("""
        INSERT INTO product_search(product_id, product_name, product_description)
        VALUES (:product_id, :product_name, :product_description)
        """),
        {
            'product_id': target.product_id,
            'product_name': target.product_name,
            'product_description': target.product_description
        }
    )
    session.commit()
    session.close()

@event.listens_for(Product, 'after_delete')
def product_after_delete(mapper, connection, target):
    session = Session(bind=connection)
    session.execute(text("""
        DELETE FROM product_search WHERE product_id = :product_id"""), {
        'product_id': target.product_id
    })
    session.commit()
    session.close()

@event.listens_for(Product, 'after_update')
def product_after_update(mapper, connection, target):
    session = Session(bind=connection)
    
    session.execute(text("""
        DELETE FROM product_search WHERE product_id = :product_id
    """), {'product_id': target.product_id})
    
    session.execute(text("""
        INSERT INTO product_search(product_id, product_name, product_description) VALUES (:product_id, :product_name, :product_description)
    """), {'product_id': target.product_id, 'product_name': target.product_name,'product_description': target.product_description})
    
    session.commit()
    session.close()
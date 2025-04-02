from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# User Model (stores user details)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


# Restaurant Model (stores restaurant details)
class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cuisine = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))

    # Relationship with Menu (ensure the foreign key is correctly linked)
    menus = db.relationship('Menu', backref='restaurant', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f"<Restaurant id={self.id} name={self.name}>"


# Menu Model (stores menu items)
class Menu(db.Model):
    __tablename__ = 'menus'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)

    # Foreign key to link menu to restaurant
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    img_url = db.Column(db.String(200))

    def __repr__(self):
        return f"<Menu id={self.id} name={self.name}>"

# Review Model (stores reviews for restaurants)
class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


# Cart Model (stores the user's cart)
class Cart(db.Model):
    __tablename__ = 'carts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Use a unique backref name to avoid conflicts
    items = db.relationship('CartItem', backref='cart_ref', lazy=True)

    def __repr__(self):
        return f"<Cart id={self.id} user_id={self.user_id}>"


class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)  # Primary Key
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)  # FK to carts.id
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menus.id'), nullable=False)  # FK to menus.id
    quantity = db.Column(db.Integer, default=1, nullable=False)

    # Use a unique backref name to avoid conflicts
    menu_item = db.relationship('Menu', backref='cart_item_links', lazy=True)

    def __repr__(self):
        return f"<CartItem id={self.id} cart_id={self.cart_id} menu_item_id={self.menu_item_id} quantity={self.quantity}>"

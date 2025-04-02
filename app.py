from flask import Flask, render_template, flash, redirect, request, url_for, session,jsonify,get_flashed_messages
from flask_session import Session
from werkzeug.utils import secure_filename
import os
from models.database import db, Restaurant, User, Menu, Review, Cart, CartItem
from datetime import datetime
from sqlalchemy import func

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = '123456789'  # Secret key for flashing messages

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zomato.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True


# File upload configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Folder where uploaded images will be stored
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed file extensions for images
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'your_secret_key'
Session(app)

# Bind the db object to the app
db.init_app(app)

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Home Route - Display All Restaurants
@app.route('/')
def index():
    restaurants = Restaurant.query.all()
    return render_template('index.html', restaurants=restaurants)

# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('signup'))

        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Signup successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    get_flashed_messages()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Fetch user
        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            session['email'] = email  # Store email in session
            session['user_id'] = user.id  # Store user_id in session

            # Clear previous messages before flashing a new one
            session.pop('_flashes', None)

            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            session.pop('_flashes', None)  # Clear flashes
            flash('Invalid credentials.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    if 'user_id' in session:
        # Clean up cart items belonging to the logged-out user
        user_id = session['user_id']
        cart = Cart.query.filter_by(user_id=user_id).first()
        if cart:
            CartItem.query.filter_by(cart_id=cart.id).delete()
            db.session.commit()
            print("[DEBUG] Cleared items from cart on logout.")

    # Clear session
    session.clear()
    flash('You have logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')


# Restaurant Details Route
@app.route('/restaurant/<int:restaurant_id>')
def restaurant_details(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    menu_items = Menu.query.filter_by(restaurant_id=restaurant_id).all()
    return render_template(
        'restaurant_details.html',
        restaurant=restaurant,
        menu_items=menu_items,
        image_url=restaurant.image_url
    )

# Admin Dashboard Route
@app.route('/admin')
def admin_dashboard():
    if 'email' not in session or session['email'] != 'hemanthbubby007@gmail.com':
        flash('You are not authorized to access the admin dashboard.', 'danger')
        return redirect(url_for('index'))
    restaurants = Restaurant.query.all()
    return render_template('admin_dashboard.html', restaurants=restaurants)


# Add Restaurant Route
@app.route('/admin/add-restaurant', methods=['GET', 'POST'])
def add_restaurant():
    if request.method == 'POST':
        name = request.form['name']
        cuisine = request.form['cuisine']
        address = request.form['address']
        rating = float(request.form['rating'])
        image_url = request.form['image_url']

        new_restaurant = Restaurant(
            name=name,
            cuisine=cuisine,
            address=address,
            rating=rating,
            image_url=image_url
        )

        db.session.add(new_restaurant)
        db.session.commit()

        flash('Restaurant added successfully!', 'success')
        return redirect(url_for('add_menu', restaurant_id=new_restaurant.id))

    return render_template('add_restaurant.html')

# Add Menu Item Route
@app.route('/admin/add-menu/<int:restaurant_id>', methods=['GET', 'POST'])
def add_menu(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        category = request.form.get('category')

        if not name or not description or not price or not category:
            flash('Please fill out all fields!', 'danger')
            return redirect(url_for('add_menu', restaurant_id=restaurant.id))

        image = request.files.get('img_url')
        image_filename = None

        if image and allowed_file(image.filename):
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        new_menu_item = Menu(
            name=name,
            description=description,
            price=float(price),
            category=category,
            restaurant_id=restaurant.id,
            img_url=f'uploads/{image_filename}' if image_filename else None
        )

        db.session.add(new_menu_item)
        db.session.commit()

        flash('Menu item added successfully!', 'success')
        return redirect(url_for('add_menu', restaurant_id=restaurant.id))

    return render_template('add_menu.html', restaurant=restaurant)

# Add to Cart Route
@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        return {'status': 'error', 'message': 'User not logged in'}, 400

    data = request.get_json()
    item_id = data.get('item_id')
    if not item_id:
        return {'status': 'error', 'message': 'Invalid item_id'}, 400

    user_id = session['user_id']
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()

    # Check if the item already exists in the cart
    cart_item = CartItem.query.filter_by(cart_id=cart.id, menu_item_id=item_id).first()
    if cart_item:
        cart_item.quantity += 1  # Increment quantity if it exists
    else:
        menu_item = Menu.query.get(item_id)
        if not menu_item:
            return {'status': 'error', 'message': 'Menu item not found'}, 404
        cart_item = CartItem(cart_id=cart.id, menu_item_id=item_id, quantity=1)
        db.session.add(cart_item)

    db.session.commit()
    print(f"[DEBUG] Item added to cart: Cart ID {cart.id}, Item ID {item_id}")
    return {'status': 'success'}, 200




# View Cart Route
@app.route('/cart')
def view_cart():
    if 'user_id' not in session:
        return {'status': 'error', 'message': 'User not logged in'}, 400

    user_id = session['user_id']
    cart = Cart.query.filter_by(user_id=user_id).first()

    if not cart:
        return {'status': 'error', 'message': 'Cart is empty'}, 400

    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    items = []
    total = 0
    for item in cart_items:
        menu_item = Menu.query.get(item.menu_item_id)
        items.append({
            'id': item.id,
            'name': menu_item.name,
            'price': menu_item.price,
            'quantity': item.quantity,
        })
        total += menu_item.price * item.quantity

    return render_template('cart.html', cart_items=items, total=total)

# Update Cart Route (Increase/Decrease Quantity)
@app.route('/update-cart', methods=['POST'])
def update_cart():
    data = request.json
    item_id = data.get('item_id')
    action = data.get('action')

    # Fetch the CartItem from DB
    cart_item = CartItem.query.get(item_id)
    if not cart_item:
        return jsonify({"status": "error", "message": "Item not found"}), 404

    # Update the quantity based on action
    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease' and cart_item.quantity > 1:
        cart_item.quantity -= 1
    elif action == 'decrease':
        return jsonify({"status": "error", "message": "Quantity cannot be less than 1"}), 400

    db.session.commit()

    # Recalculate total price
    cart = cart_item.cart_ref
    total = sum(item.quantity * item.menu_item.price for item in cart.items)

    return jsonify({"status": "success", "total": total})


@app.route('/search')
def search():
    query = request.args.get('query', '').strip()  # Get the search term from the query string
    if not query:
        flash('Please enter a search term.', 'danger')
        return redirect(url_for('index'))

    # Filter restaurants by name or cuisine
    results = Restaurant.query.filter(
        (Restaurant.name.ilike(f'%{query}%')) |
        (Restaurant.cuisine.ilike(f'%{query}%'))
    ).all()

    return render_template('search_results.html', query=query, results=results)

@app.route('/remove-item', methods=['POST'])
def remove_item():
    data = request.json
    item_id = data.get('item_id')

    # Fetch and delete the CartItem
    cart_item = CartItem.query.get(item_id)
    if not cart_item:
        return jsonify({"status": "error", "message": "Item not found"}), 404

    cart = cart_item.cart_ref
    db.session.delete(cart_item)
    db.session.commit()

    # Recalculate total price
    total = sum(item.quantity * item.menu_item.price for item in cart.items)
    return jsonify({"status": "success", "total": total, "cart_empty": len(cart.items) == 0})


@app.route('/admin/edit-restaurant/<int:restaurant_id>', methods=['GET', 'POST'])
def edit_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)

    if request.method == 'POST':
        restaurant.name = request.form['name']
        restaurant.cuisine = request.form['cuisine']
        restaurant.address = request.form['address']
        restaurant.rating = float(request.form['rating'])
        restaurant.image_url = request.form['image_url']

        db.session.commit()
        flash('Restaurant updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_restaurant.html', restaurant=restaurant)


@app.route('/admin/delete-restaurant/<int:restaurant_id>', methods=['POST'])
def delete_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    db.session.delete(restaurant)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/api/restaurant-data', methods=['GET'])
def get_restaurant_data():
    # Fetch total number of restaurants
    total_restaurants = Restaurant.query.count()

    # Fetch ratings grouped by value
    ratings = db.session.query(Restaurant.rating, db.func.count(Restaurant.id)) \
        .group_by(Restaurant.rating).all()

    # Format data for the chart
    ratings_data = [{"rating": r[0], "count": r[1]} for r in ratings]

    return jsonify({
        "total_restaurants": total_restaurants,
        "ratings_data": ratings_data
    })

@app.route('/admin/restaurant-list', methods=['GET'])
def restaurant_list():
    restaurants = Restaurant.query.all()  # Fetch all restaurants from the database
    return render_template('restaurant_list.html', restaurants=restaurants)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        flash('You must be logged in to checkout.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']
    cart = Cart.query.filter_by(user_id=user_id).first()

    if not cart:
        flash('Your cart is empty.', 'danger')
        return redirect(url_for('view_cart'))

    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    items = []
    total = 0

    for item in cart_items:
        menu_item = Menu.query.get(item.menu_item_id)
        if menu_item:
            items.append({
                'id': item.id,
                'name': menu_item.name,
                'price': menu_item.price,
                'quantity': item.quantity,
            })
            total += menu_item.price * item.quantity

    if request.method == 'POST':
        # Retrieve form data
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        landmark = request.form['landmark']
        payment_method = request.form['payment_method']

        # You can process the order here (e.g., save to database)
        flash('Order placed successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('checkout.html', cart_items=items, total=total)


@app.route('/filter_rating', methods=['GET'])
def filter_rating():
    rating = request.args.get('rating', type=float)
    if rating:
        filtered_restaurants = Restaurant.query.filter(Restaurant.rating >= rating).all()
    else:
        filtered_restaurants = Restaurant.query.all()

    restaurants_data = [{
        'id': restaurant.id,
        'name': restaurant.name,
        'rating': restaurant.rating,
        'cuisine': restaurant.cuisine,
        'image_url': restaurant.image_url
    } for restaurant in filtered_restaurants]

    return jsonify(restaurants_data)


# Run the Flask App
if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    with app.app_context():
        db.create_all()  # Ensure tables are created
    app.run(host='127.0.0.1', port=5001,
        debug=True)


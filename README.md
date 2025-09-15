# Zomato Clone

## 📖 Project Explanation

This is a **Zomato Clone** — a simplified version of the popular food delivery app, built for learning purposes. The project demonstrates how to create an online restaurant listing and ordering system using **Django** as the backend framework.

### ✅ Key Features
- **User Authentication:** Users can sign up, log in, and manage their account.
- **Restaurant Listing:** Browse through a limited list of up to 50 restaurants.
- **Menu Viewing:** See detailed menus for each restaurant.
- **Order Placement:** Select menu items and place an order.
- **Order Confirmation:** Users receive confirmation once the order is placed.

### 🛠 Technologies Used
- **Backend:** Django framework
- **Database:** SQLite (for storing user data, restaurants, menus, and orders)
- **Frontend:** HTML, CSS, and JavaScript
- **Authentication:** Django’s built-in user authentication system

### 🔍 How It Works
1. The user signs up or logs into the application.
2. Upon login, the user is shown a list of restaurants (limited to 50 for simplicity).
3. The user can click on a restaurant to view its menu items.
4. Menu items can be selected and added to an order.
5. The user can place the order, and an order confirmation is displayed.

### 📂 Project Structure
- `models.py`: Contains database models for restaurants, menu items, and orders.
- `views.py`: Handles application logic such as listing restaurants and placing orders.
- `templates/`: Contains HTML templates for rendering pages.
- `static/`: Contains CSS and JavaScript files for styling and interactivity.

### 📸 Screenshots

#### Restaurant Listing
![Login Page](pscreenshots/home.png.png)

#### Restaurant Menu page
![Restaurant Listing](pscreenshots/menu.png.png)

#### Cart
![Menu Page](pscreenshots/cart.png.png)

#### Checkout Page
![Order Confirmation](pscreenshots/checkout.png.png)

> Make sure to replace the image paths like `screenshots/login.png` with the correct file paths where your screenshots are saved in the project.

### 🚀 Future Enhancements
- Add payment gateway integration.
- Implement filters for cuisine, price, or ratings.
- Enhance UI with responsive design.
- Deploy the project to a live server.

---

Feel free to explore, modify, and expand this project to enhance your understanding of web development using Django!

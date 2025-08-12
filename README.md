
# Grocery Store

**Grocery Store** is a multi-user web application that allows customers to explore and purchase products, while sellers can register and list their own items. The application also provides **REST APIs** for products, categories, and users, designed in accordance with **OpenAPI specifications**.

---

## 🚀 Technologies Used

- **Python** – Primary programming language for application development  
- **HTML/CSS** – Structure and styling of web pages  
- **Jinja2** – Dynamic data rendering in HTML templates  
- **Bootstrap** – CSS framework for responsive and visually appealing designs  
- **SQLite** – Application database  
- **Flask** – Web framework for the application, with the following extensions:
  - **Flask-RESTful** – Building RESTful APIs
  - **Flask-SQLAlchemy** – ORM for database interaction
  - **Flask-CORS** – Enabling cross-origin requests
  - **Flask-Login** – User authentication and session management
  - **Flask-JWT-Extended** – Token-based authentication for API endpoints  
- **Matplotlib** – Visualizing most demanded products and categories

---

## 📡 API Design

The REST APIs, built using **Flask-RESTful**, perform CRUD operations on:
- **Product**
- **Category**
- **User** tables  

Authentication & authorization for API endpoints are handled with **Flask-JWT-Extended** using **JSON Web Tokens (JWT)**.  

📄 Detailed API documentation is available in the openapi.yaml file.
---
## 🏗 Architecture & Features

The application follows the **MVC (Model–View–Controller)** architecture:  
- **Model** – Python classes mapped to SQLite database tables using Flask-SQLAlchemy  
- **View** – HTML/CSS with Bootstrap for the frontend  
- **Controller** – Python + Flask for request handling and application logic  

### ✨ Features

#### Authentication
- User and Admin signup/login
- Token-based authentication for APIs

#### Admin
- Create, view, update, and delete products or categories

#### User
- Browse products and categories
- Add products to cart, update quantities, or remove items
- Search products/categories using **FTS5** by:
  - Product name
  - Product description
  - Category name

#### API Security
- Frontend & backend validation before database operations
- Protected endpoints using JWT

---

## ⚙️ How to Run the Application

1. Clone the project:
   ```bash
   git clone https://github.com/ikrlalit/Grocery-Store.git
2. Next move to project directory:
   ```bash
   cd Grocery-Store
3. Create a virtual environment:
   ```bash
   python3 -m venv .venv
4. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
5. Install dependecies:
   ```bash
   pip install -r requirements.txt
6. Run the application:
   ```bash
   python app.py
---
**Video Demo**: [here](https://youtu.be/dFpiXiBLxGQ)

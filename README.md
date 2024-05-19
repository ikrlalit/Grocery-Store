
# Grocery Store


The grocery store is a multi-user web application that allows users to explore and buy listed products. Similarly, sellers can register and list their products on it. The Rest APIs fro products, categories and user are also developed which follows the OpenAPI specifications.

## Technologies Used:
* Python – Python is the primary programming language used for developing app
* HTML/CSS – For creating web pages and styling them
* Jinja2 – Used for displaying data dynamically in HTML pages
* Bootstrap – It is a CSS framework, we used for making pages visually appealing
* SQLite- Serves as the database for the application
* Python Flask – Serves as the web framework for the app, it utilizes the following libraries. 
* Flask-Restful – Used for developing Restful APIs
    * Flask-SQLAlchemy – For creating models that allows application to interact with database
    * Flask-CORS – Used for allowing cross-origin requests for APIs
    * Flask-Login – Used for implementing login functionality to the application
    * Flask-JWT-Extended – Used for implementing token-based authentication for API end points
* Matplotlib- To create charts of the most demanded products and categories

## API Design:
The APIs are designed using Flask-Restful for performing CRUD on product, category, and user tables. We used the flask-jwt-extended package for implementing authentication and authorization on API endpoints. For more details, please refer to the openapi.yaml file.

## Architecture and Features:
The application follows the standard MVC architecture. The View of the application is created using HTML/CSS, and Bootstrap. The Controller is created using Python and Flask. Models are the Python classes that map with SQLite database tables using the Flask-SQLAlchemy ORM library.
The features of the application are as follows-
* Signup and Login for User and Admin
* An admin can view, create, update, and delete a product or category
* A user can view, add, increase/ decrease the item quantity, or delete a product from the cart. Users can search for a product or category and add it to the cart
* Search feature is implemented using FTS5 and allow searching by product name, product description, or category name
* APIs for performing CRUD on product, category, and user tables. The endpoints are protected using JSON Web Token 
* Frontend as well as backend validation on APIs of input fields before storing/ selecting from the database

## Instructions to Run the Application
* Open your terminal
* cd into the directory where app.py is located
* Use ```python3 -m venv .venv``` to create the virtual environment
* Once created use ```source .venv/bin/activate``` this will activate virutal environment
* Next execute the ```pip install -r requirements.txt``` this will install all the packages required for running the application
* Finally run the app using ```python app.py```

**Video Demo**: [here](https://youtu.be/dFpiXiBLxGQ)


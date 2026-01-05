from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from bson import ObjectId
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from functools import wraps
from flasgger import Swagger

load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['JWT_ALGORITHM'] = 'HS256'

CORS(app)
jwt = JWTManager(app)

# Swagger configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Local Pharmacy API",
        "description": "API documentation for Local Pharmacy - Full-stack pharmacy management system",
        "version": "1.0.0",
        "contact": {
            "name": "API Support",
            "email": "admin@localpharmacy.com"
        }
    },
    "basePath": "/api",
    "schemes": ["http", "https"],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
        }
    },
    "tags": [
        {
            "name": "Products",
            "description": "Product management endpoints"
        },
        {
            "name": "Orders",
            "description": "Order management endpoints"
        },
        {
            "name": "Offers",
            "description": "Offer code management endpoints"
        },
        {
            "name": "Admin",
            "description": "Admin authentication and dashboard endpoints"
        },
        {
            "name": "Users",
            "description": "User management endpoints (admin only)"
        },
        {
            "name": "Customers",
            "description": "Customer registration and authentication endpoints"
        },
        {
            "name": "Testimonials",
            "description": "Customer testimonials and reviews endpoints"
        },
        {
            "name": "Callback Requests",
            "description": "Callback request management endpoints"
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# MongoDB connection - Lazy initialization to avoid connection during import (for CI/testing)
MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://username:password@cluster.mongodb.net/pharmacy?retryWrites=true&w=majority')
client = None
db = None

# Collections - Will be initialized when get_db() is called
products_collection = None
orders_collection = None
offers_collection = None
users_collection = None  # Unified collection for both admin and customer users
testimonials_collection = None
callback_requests_collection = None

def get_db():
    """Initialize MongoDB connection lazily. This allows imports to succeed without MongoDB connection."""
    global client, db, products_collection, orders_collection, offers_collection
    global users_collection, testimonials_collection, callback_requests_collection
    
    if client is None:
        # Only connect if MONGO_URI is set and not a placeholder
        if not MONGO_URI or 'username:password' in MONGO_URI:
            raise ConnectionError("MONGO_URI not configured. Please set MONGO_URI environment variable.")
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            db = client.pharmacy
            
            # Initialize collections
            products_collection = db.products
            orders_collection = db.orders
            offers_collection = db.offers
            users_collection = db.users  # Unified collection for admin and customer
            testimonials_collection = db.testimonials
            callback_requests_collection = db.callback_requests
        except Exception as e:
            # If connection fails during import (e.g., in CI), allow import to succeed
            # Connection will be retried when app actually runs
            if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
                print(f"Warning: MongoDB connection skipped in CI environment: {e}")
            else:
                raise
    
    return db

# Initialize admin user if not exists (only when actually running, not during import)
def init_admin():
    """Initialize admin user. Only runs when database is actually accessed."""
    try:
        get_db()  # Ensure database is connected
        if users_collection and users_collection.count_documents({'role': 'admin'}) == 0:
            users_collection.insert_one({
                'username': 'admin',
                'password': generate_password_hash('admin123'),
                'email': 'admin@pharmacy.com',
                'role': 'admin',
                'created_at': datetime.utcnow()
            })
            print("Default admin created: username='admin', password='admin123'")
    except (ConnectionError, Exception) as e:
        # Silently fail during import/testing - will be initialized when app actually runs
        if not (os.getenv('CI') or os.getenv('GITHUB_ACTIONS')):
            print(f"Warning: Could not initialize admin: {e}")

# Don't call init_admin() at import time - will be called when app starts

# Helper function to convert ObjectId to string
def serialize_doc(doc):
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

# Role-based access control decorators
def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()
            user = users_collection.find_one({'username': current_user})
            if not user or user.get('role') not in allowed_roles:
                return jsonify({'message': f'Access denied. Required roles: {", ".join(allowed_roles)}'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Admin only decorator
def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        try:
            user = users_collection.find_one({'_id': ObjectId(user_id)})
        except:
            # Fallback for old username-based tokens
            user = users_collection.find_one({'username': user_id})
        
        if not user or user.get('role') != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROOT ROUTE ====================

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'Local Pharmacy API',
        'version': '1.0.0',
        'endpoints': {
            'products': '/api/products',
            'orders': '/api/orders',
            'offers': '/api/offers',
            'admin': '/api/admin'
        }
    }), 200

# ==================== AUTH ROUTES ====================

@app.route('/api/login', methods=['POST'])
def unified_login():
    """
    Unified Login
    ---
    tags:
      - Auth
    summary: Authenticate user (admin or customer)
    description: Unified login endpoint for both admin and customer users. Returns JWT token and user role on successful authentication.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - identifier
            - password
          properties:
            identifier:
              type: string
              description: Username (for admin) or phone number (for customer)
              example: admin or +919876543210
            password:
              type: string
              example: password123
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            access_token:
              type: string
            user_id:
              type: string
            username:
              type: string
            name:
              type: string
            email:
              type: string
            phone:
              type: string
            role:
              type: string
              enum: [admin, customer]
      400:
        description: Missing identifier or password
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    identifier = data.get('identifier')  # Can be username or phone
    password = data.get('password')
    
    if not identifier or not password:
        return jsonify({'message': 'Identifier (username/phone) and password required'}), 400
    
    # Try to find user by username first (for admin)
    user = users_collection.find_one({'username': identifier})
    
    # If not found by username, try by phone (for customer)
    if not user:
        user = users_collection.find_one({'phone': identifier})
    
    if user and check_password_hash(user['password'], password):
        user_id = str(user['_id'])
        access_token = create_access_token(identity=user_id)
        
        response_data = {
            'access_token': access_token,
            'user_id': user_id,
            'role': user.get('role', 'customer')
        }
        
        # Add role-specific fields
        if user.get('role') == 'admin':
            response_data['username'] = user.get('username')
        else:  # customer
            response_data['name'] = user.get('name')
            response_data['email'] = user.get('email')
            response_data['phone'] = user.get('phone')
            if user.get('username'):
                response_data['username'] = user.get('username')
        
        return jsonify(response_data), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """
    Verify Token
    ---
    tags:
      - Auth
    summary: Verify JWT token
    description: Verify if the current JWT token is valid and return user information.
    security:
      - Bearer: []
    responses:
      200:
        description: Token is valid
        schema:
          type: object
          properties:
            user_id:
              type: string
            username:
              type: string
            name:
              type: string
            email:
              type: string
            phone:
              type: string
            role:
              type: string
      401:
        description: Invalid or expired token
      404:
        description: User not found
    """
    user_id = get_jwt_identity()
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if user:
        response_data = {
            'user_id': str(user['_id']),
            'role': user.get('role', 'customer')
        }
        
        if user.get('role') == 'admin':
            response_data['username'] = user.get('username')
        else:  # customer
            response_data['name'] = user.get('name')
            response_data['email'] = user.get('email')
            response_data['phone'] = user.get('phone')
            if user.get('username'):
                response_data['username'] = user.get('username')
        
        return jsonify(response_data), 200
    return jsonify({'message': 'User not found'}), 404

# Keep old admin login for backward compatibility (deprecated)
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """
    Admin Login (Deprecated - Use /api/login instead)
    ---
    tags:
      - Admin
    summary: Authenticate admin user (Deprecated)
    description: DEPRECATED - Use /api/login instead. Login endpoint for admin users.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': 'Username and password required'}), 400
    
    # Use unified login logic
    user = users_collection.find_one({'username': username})
    if user and check_password_hash(user['password'], password):
        user_id = str(user['_id'])
        access_token = create_access_token(identity=user_id)
        return jsonify({
            'access_token': access_token,
            'username': username,
            'role': user.get('role', 'admin')
        }), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/admin/verify', methods=['GET'])
@jwt_required()
def verify_admin_token():
    """
    Verify Admin Token (Deprecated - Use /api/verify instead)
    ---
    tags:
      - Admin
    summary: Verify JWT token (Deprecated)
    description: DEPRECATED - Use /api/verify instead.
    """
    user_id = get_jwt_identity()
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if user:
        response_data = {
            'username': user.get('username'),
            'role': user.get('role', 'admin')
        }
        return jsonify(response_data), 200
    return jsonify({'message': 'User not found'}), 404

# ==================== CUSTOMER AUTH ROUTES ====================

@app.route('/api/register', methods=['POST'])
def register():
    """
    User Registration
    ---
    tags:
      - Auth
    summary: Register a new user
    description: Register a new user account. By default, all registrations are created with 'customer' role.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - phone
            - password
          properties:
            name:
              type: string
              example: John Doe
            email:
              type: string
              example: john@example.com
            phone:
              type: string
              example: "+919876543210"
            password:
              type: string
              example: password123
            address:
              type: string
              example: "123 Main St, City"
    responses:
      201:
        description: User registered successfully
        schema:
          type: object
          properties:
            message:
              type: string
            user_id:
              type: string
            access_token:
              type: string
            name:
              type: string
            email:
              type: string
            phone:
              type: string
            role:
              type: string
      400:
        description: Missing required fields or user already exists
    """
    data = request.get_json()
    required_fields = ['name', 'email', 'phone', 'password']
    
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields: name, email, phone, password'}), 400
    
    # Check if user already exists
    existing_user = users_collection.find_one({
        '$or': [
            {'email': data['email']},
            {'phone': data['phone']}
        ]
    })
    if existing_user:
        return jsonify({'message': 'Email or phone already exists'}), 400
    
    # Create user with default role 'customer'
    user = {
        'name': data['name'],
        'email': data['email'],
        'phone': data['phone'],
        'password': generate_password_hash(data['password']),
        'address': data.get('address', ''),
        'role': 'customer',  # Default role
        'created_at': datetime.utcnow()
    }
    
    result = users_collection.insert_one(user)
    user_id = str(result.inserted_id)
    
    # Create access token
    access_token = create_access_token(identity=user_id)
    
    return jsonify({
        'message': 'User registered successfully',
        'user_id': user_id,
        'access_token': access_token,
        'name': user['name'],
        'email': user['email'],
        'phone': user['phone'],
        'role': user['role']
    }), 201

# Keep old customer register for backward compatibility
@app.route('/api/customers/register', methods=['POST'])
def customer_register():
    """Deprecated - Use /api/register instead"""
    return register()

@app.route('/api/customers/login', methods=['POST'])
def customer_login():
    """Deprecated - Use /api/login instead"""
    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')
    
    if not phone or not password:
        return jsonify({'message': 'Phone number and password required'}), 400
    
    # Use unified login logic
    user = users_collection.find_one({'phone': phone, 'role': 'customer'})
    if user and check_password_hash(user['password'], password):
        user_id = str(user['_id'])
        access_token = create_access_token(identity=user_id)
        return jsonify({
            'access_token': access_token,
            'customer_id': user_id,
            'name': user['name'],
            'email': user['email'],
            'phone': user['phone']
        }), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/customers/verify', methods=['GET'])
@jwt_required()
def verify_customer_token():
    """Deprecated - Use /api/verify instead"""
    user_id = get_jwt_identity()
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if user:
        return jsonify({
            'customer_id': str(user['_id']),
            'name': user.get('name'),
            'email': user.get('email'),
            'phone': user.get('phone')
        }), 200
    return jsonify({'message': 'User not found'}), 404

# ==================== USER MANAGEMENT ROUTES ====================

@app.route('/api/users', methods=['POST'])
@admin_required
def create_user():
    """
    Create User
    ---
    tags:
      - Users
    summary: Create a new user with role
    description: Admin endpoint to create new users (admin, driver, helper, etc.)
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
            - role
          properties:
            username:
              type: string
              example: driver1
            password:
              type: string
              example: password123
            email:
              type: string
              example: driver1@pharmacy.com
            role:
              type: string
              enum: [admin, driver, helper]
              example: driver
    responses:
      201:
        description: User created successfully
        schema:
          type: object
          properties:
            _id:
              type: string
            username:
              type: string
            email:
              type: string
            role:
              type: string
      400:
        description: Missing required fields or user already exists
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Missing required fields: username, password, role"
      403:
        description: Admin access required
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Admin access required"
    """
    data = request.get_json()
    required_fields = ['username', 'password', 'role']
    
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields: username, password, role'}), 400
    
    if data['role'] not in ['admin', 'driver', 'helper']:
        return jsonify({'message': 'Invalid role. Allowed roles: admin, driver, helper'}), 400
    
    # Check if user already exists
    existing_user = users_collection.find_one({'username': data['username']})
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 400
    
    user = {
        'username': data['username'],
        'password': generate_password_hash(data['password']),
        'email': data.get('email', ''),
        'role': data['role'],
        'created_at': datetime.utcnow()
    }
    
    result = users_collection.insert_one(user)
    user['_id'] = str(result.inserted_id)
    user.pop('password', None)  # Don't return password
    return jsonify(serialize_doc(user)), 201

@app.route('/api/users', methods=['GET'])
@admin_required
def get_users():
    """
    Get All Users
    ---
    tags:
      - Users
    summary: Get all users
    description: Admin endpoint to retrieve list of all users with their roles
    security:
      - Bearer: []
    parameters:
      - in: query
        name: role
        type: string
        required: false
        description: Filter users by role
        enum: [admin, driver, helper]
    responses:
      200:
        description: List of users
        schema:
          type: array
          items:
            type: object
            properties:
              _id:
                type: string
              username:
                type: string
              email:
                type: string
              role:
                type: string
              created_at:
                type: string
      403:
        description: Admin access required
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Admin access required"
    """
    role_filter = request.args.get('role', '')
    query = {}
    if role_filter:
        query = {'role': role_filter}
    
    users = list(users_collection.find(query).sort('username', 1))
    # Remove passwords from response
    for user in users:
        user.pop('password', None)
    
    return jsonify([serialize_doc(u) for u in users]), 200

@app.route('/api/users/<user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """
    Update User
    ---
    tags:
      - Users
    summary: Update user information
    description: Admin endpoint to update user details (password, email, role)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
        description: User ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            password:
              type: string
            email:
              type: string
            role:
              type: string
              enum: [admin, driver, helper]
    responses:
      200:
        description: User updated successfully
      400:
        description: Invalid role or user ID
      404:
        description: User not found
      403:
        description: Admin access required
    """
    try:
        data = request.get_json()
        update_data = {}
        
        if 'password' in data:
            update_data['password'] = generate_password_hash(data['password'])
        if 'email' in data:
            update_data['email'] = data['email']
        if 'role' in data:
            if data['role'] not in ['admin', 'driver', 'helper']:
                return jsonify({'message': 'Invalid role'}), 400
            update_data['role'] = data['role']
        
        if not update_data:
            return jsonify({'message': 'No fields to update'}), 400
        
        result = users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'message': 'User not found'}), 404
        
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        user.pop('password', None)
        return jsonify(serialize_doc(user)), 200
    except:
        return jsonify({'message': 'Invalid user ID'}), 400

@app.route('/api/users/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """
    Delete User
    ---
    tags:
      - Users
    summary: Delete a user
    description: Admin endpoint to delete a user account
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
        description: User ID
    responses:
      200:
        description: User deleted successfully
      404:
        description: User not found
      403:
        description: Admin access required
        schema:
          type: object
          properties:
          type: array
          items:
            type: object
            properties:
              _id:
                type: string
                example: 507f1f77bcf86cd799439011
              name:
                type: string
                example: Aspirin 100mg
              description:
                type: string
                example: Pain relief medication
              price:
                type: number
                example: 5.99
              stock:
                type: integer
                example: 50
              category:
                type: string
                example: Pain Relief
              image:
                type: string
                example: https://example.com/image.jpg
    """
    search = request.args.get('search', '')
    query = {}
    if search:
        query = {
            '$or': [
                {'name': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}},
                {'category': {'$regex': search, '$options': 'i'}}
            ]
        }
    
    products = list(products_collection.find(query).sort('name', 1))
    return jsonify([serialize_doc(p) for p in products]), 200

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """
    Get Single Product
    ---
    tags:
      - Products
    summary: Get a single product by ID
    description: Retrieve detailed information about a specific product
    parameters:
      - in: path
        name: product_id
        type: string
        required: true
        description: Product ID
    responses:
      200:
        description: Product details
        schema:
          type: object
          properties:
            _id:
              type: string
            name:
              type: string
            description:
              type: string
            price:
              type: number
            stock:
              type: integer
            category:
              type: string
            image:
              type: string
      400:
        description: Invalid product ID
      404:
        description: Product not found
    """
    try:
        product = products_collection.find_one({'_id': ObjectId(product_id)})
        if product:
            return jsonify(serialize_doc(product)), 200
        return jsonify({'message': 'Product not found'}), 404
    except:
        return jsonify({'message': 'Invalid product ID'}), 400

@app.route('/api/products', methods=['POST'])
@admin_required
def create_product():
    """
    Create Product
    ---
    tags:
      - Products
    summary: Create a new product
    description: Admin endpoint to add a new product to the catalog
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - price
            - stock
          properties:
            name:
              type: string
              example: Aspirin 100mg
            description:
              type: string
              example: Pain relief medication
            price:
              type: number
              example: 5.99
            stock:
              type: integer
              example: 50
            category:
              type: string
              example: Pain Relief
            image:
              type: string
              example: https://example.com/image.jpg
    responses:
      201:
        description: Product created successfully
        schema:
          type: object
          properties:
            _id:
              type: string
            name:
              type: string
            price:
              type: number
            stock:
              type: integer
      400:
        description: Missing required fields
      403:
        description: Admin access required
    """
    data = request.get_json()
    required_fields = ['name', 'price', 'stock']
    
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    product = {
        'name': data['name'],
        'description': data.get('description', ''),
        'price': float(data['price']),
        'stock': int(data['stock']),
        'category': data.get('category', 'General'),
        'image': data.get('image', ''),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    result = products_collection.insert_one(product)
    product['_id'] = str(result.inserted_id)
    return jsonify(serialize_doc(product)), 201

@app.route('/api/products/<product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    """
    Update Product
    ---
    tags:
      - Products
    summary: Update an existing product
    description: Admin endpoint to update product information
    security:
      - Bearer: []
    parameters:
      - in: path
        name: product_id
        type: string
        required: true
        description: Product ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
            price:
              type: number
            stock:
              type: integer
            category:
              type: string
            image:
              type: string
    responses:
      200:
        description: Product updated successfully
        schema:
          type: object
          properties:
            _id:
              type: string
            name:
              type: string
            price:
              type: number
      400:
        description: Invalid product ID
      404:
        description: Product not found
      403:
        description: Admin access required
    """
    try:
        data = request.get_json()
        update_data = {
            'updated_at': datetime.utcnow()
        }
        
        if 'name' in data:
            update_data['name'] = data['name']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'price' in data:
            update_data['price'] = float(data['price'])
        if 'stock' in data:
            update_data['stock'] = int(data['stock'])
        if 'category' in data:
            update_data['category'] = data['category']
        if 'image' in data:
            update_data['image'] = data['image']
        
        result = products_collection.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'message': 'Product not found'}), 404
        
        product = products_collection.find_one({'_id': ObjectId(product_id)})
        return jsonify(serialize_doc(product)), 200
    except:
        return jsonify({'message': 'Invalid product ID'}), 400

@app.route('/api/products/<product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """
    Delete Product
    ---
    tags:
      - Products
    summary: Delete a product
    description: Admin endpoint to remove a product from the catalog
    security:
      - Bearer: []
    parameters:
      - in: path
        name: product_id
        type: string
        required: true
        description: Product ID
    responses:
      200:
        description: Product deleted successfully
      400:
        description: Invalid product ID
      404:
        description: Product not found
      403:
        description: Admin access required
    """
    try:
        result = products_collection.delete_one({'_id': ObjectId(product_id)})
        if result.deleted_count == 0:
            return jsonify({'message': 'Product not found'}), 404
        return jsonify({'message': 'Product deleted successfully'}), 200
    except:
        return jsonify({'message': 'Invalid product ID'}), 400

# ==================== ORDER ROUTES ====================

@app.route('/api/orders', methods=['POST'])
def create_order():
    """
    Create Order
    ---
    tags:
      - Orders
    summary: Create a new order
    description: Create a new customer order. Automatically applies offer codes and updates product stock.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - customer
            - items
            - total
          properties:
            customer:
              type: object
              required:
                - name
                - phone
                - address
              properties:
                name:
                  type: string
                  example: John Doe
                phone:
                  type: string
                  example: +1234567890
                address:
                  type: string
                  example: 123 Main St, City, State 12345
            items:
              type: array
              items:
                type: object
                properties:
                  product_id:
                    type: string
                  name:
                    type: string
                  price:
                    type: number
                  quantity:
                    type: integer
            total:
              type: number
              example: 50.99
            offer_code:
              type: string
              required: false
              example: SAVE10
    responses:
      201:
        description: Order created successfully
        schema:
          type: object
          properties:
            _id:
              type: string
            customer:
              type: object
            items:
              type: array
            subtotal:
              type: number
            discount:
              type: number
            total:
              type: number
            status:
              type: string
              example: pending
      400:
        description: Missing required fields or invalid data
    """
    data = request.get_json()
    required_fields = ['customer', 'items', 'total']
    
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Validate customer data
    customer = data['customer']
    if not all(k in customer for k in ['name', 'phone', 'address']):
        return jsonify({'message': 'Customer details incomplete'}), 400
    
    # Apply offer code if provided
    final_total = float(data['total'])
    offer_code = data.get('offer_code', '')
    discount = 0
    
    if offer_code:
        offer = offers_collection.find_one({'code': offer_code, 'active': True})
        if offer:
            if offer['type'] == 'percentage':
                discount = final_total * (offer['value'] / 100)
            else:
                discount = offer['value']
            final_total = max(0, final_total - discount)
    
    order = {
        'customer': customer,
        'items': data['items'],
        'subtotal': float(data['total']),
        'discount': discount,
        'total': final_total,
        'offer_code': offer_code if offer_code else None,
        'status': 'pending',
        'created_at': datetime.utcnow()
    }
    
    result = orders_collection.insert_one(order)
    order['_id'] = str(result.inserted_id)
    
    # Update product stock
    for item in data['items']:
        products_collection.update_one(
            {'_id': ObjectId(item['product_id'])},
            {'$inc': {'stock': -item['quantity']}}
        )
    
    return jsonify(serialize_doc(order)), 201

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """
    Get Orders
    ---
    tags:
      - Orders
    summary: Get all orders
    description: Retrieve orders. Supports filtering by phone number for customer order history.
    parameters:
      - in: query
        name: phone
        type: string
        required: false
        description: Filter orders by customer phone number
        example: +1234567890
    responses:
      200:
        description: List of orders
        schema:
          type: array
          items:
            type: object
            properties:
              _id:
                type: string
              customer:
                type: object
              items:
                type: array
              total:
                type: number
              status:
                type: string
    """
    phone = request.args.get('phone', '')
    
    if phone:
        orders = list(orders_collection.find({'customer.phone': phone}).sort('created_at', -1))
    else:
        orders = list(orders_collection.find({}).sort('created_at', -1))
    
    return jsonify([serialize_doc(o) for o in orders]), 200

@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """
    Get Single Order
    ---
    tags:
      - Orders
    summary: Get a single order by ID
    description: Retrieve detailed information about a specific order
    parameters:
      - in: path
        name: order_id
        type: string
        required: true
        description: Order ID
    responses:
      200:
        description: Order details
        schema:
          type: object
          properties:
            _id:
              type: string
            customer:
              type: object
            items:
              type: array
            total:
              type: number
            status:
              type: string
      400:
        description: Invalid order ID
      404:
        description: Order not found
    """
    try:
        order = orders_collection.find_one({'_id': ObjectId(order_id)})
        if order:
            return jsonify(serialize_doc(order)), 200
        return jsonify({'message': 'Order not found'}), 404
    except:
        return jsonify({'message': 'Invalid order ID'}), 400

@app.route('/api/orders/<order_id>', methods=['PUT'])
@admin_required
def update_order_status(order_id):
    """
    Update Order Status
    ---
    tags:
      - Orders
    summary: Update order status
    description: Admin endpoint to update the status of an order
    security:
      - Bearer: []
    parameters:
      - in: path
        name: order_id
        type: string
        required: true
        description: Order ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
              enum: [pending, confirmed, processing, shipped, delivered, cancelled]
              example: confirmed
    responses:
      200:
        description: Order status updated successfully
        schema:
          type: object
          properties:
            _id:
              type: string
            status:
              type: string
      400:
        description: Invalid status or order ID
      404:
        description: Order not found
      403:
        description: Admin access required
    """
    try:
        data = request.get_json()
        status = data.get('status')
        
        if status not in ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']:
            return jsonify({'message': 'Invalid status'}), 400
        
        result = orders_collection.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': {'status': status, 'updated_at': datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            return jsonify({'message': 'Order not found'}), 404
        
        order = orders_collection.find_one({'_id': ObjectId(order_id)})
        return jsonify(serialize_doc(order)), 200
    except:
        return jsonify({'message': 'Invalid order ID'}), 400

# ==================== OFFER ROUTES ====================

@app.route('/api/offers', methods=['GET'])
def get_offers():
    """
    Get Offers
    ---
    tags:
      - Offers
    summary: Get all offers
    description: Retrieve all offer codes. Supports filtering by active status.
    parameters:
      - in: query
        name: active
        type: string
        required: false
        description: Filter by active status (true/false)
        example: true
    responses:
      200:
        description: List of offers
        schema:
          type: array
          items:
            type: object
            properties:
              _id:
                type: string
              code:
                type: string
              type:
                type: string
                enum: [percentage, fixed]
              value:
                type: number
              active:
                type: boolean
    """
    active_only = request.args.get('active', 'true').lower() == 'true'
    query = {'active': True} if active_only else {}
    offers = list(offers_collection.find(query).sort('created_at', -1))
    return jsonify([serialize_doc(o) for o in offers]), 200

@app.route('/api/offers/<offer_code>', methods=['GET'])
def get_offer(offer_code):
    """
    Get Offer by Code
    ---
    tags:
      - Offers
    summary: Get an offer by code
    description: Retrieve offer details by offer code
    parameters:
      - in: path
        name: offer_code
        type: string
        required: true
        description: Offer code
        example: SAVE10
    responses:
      200:
        description: Offer details
        schema:
          type: object
          properties:
            _id:
              type: string
            code:
              type: string
            type:
              type: string
            value:
              type: number
            active:
              type: boolean
      404:
        description: Offer not found or inactive
    """
    offer = offers_collection.find_one({'code': offer_code, 'active': True})
    if offer:
        return jsonify(serialize_doc(offer)), 200
    return jsonify({'message': 'Offer not found or inactive'}), 404

@app.route('/api/offers', methods=['POST'])
@admin_required
def create_offer():
    """
    Create Offer
    ---
    tags:
      - Offers
    summary: Create a new offer code
    description: Admin endpoint to create promotional offer codes
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - code
            - type
            - value
          properties:
            code:
              type: string
              example: SAVE10
            type:
              type: string
              enum: [percentage, fixed]
              example: percentage
            value:
              type: number
              example: 10
            description:
              type: string
              example: 10% off on all products
            active:
              type: boolean
              example: true
    responses:
      201:
        description: Offer created successfully
        schema:
          type: object
          properties:
            _id:
              type: string
            code:
              type: string
            type:
              type: string
            value:
              type: number
      400:
        description: Missing required fields or code already exists
      403:
        description: Admin access required
    """
    data = request.get_json()
    required_fields = ['code', 'type', 'value']
    
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    if data['type'] not in ['percentage', 'fixed']:
        return jsonify({'message': 'Invalid offer type'}), 400
    
    # Check if code already exists
    existing = offers_collection.find_one({'code': data['code']})
    if existing:
        return jsonify({'message': 'Offer code already exists'}), 400
    
    offer = {
        'code': data['code'].upper(),
        'type': data['type'],
        'value': float(data['value']),
        'description': data.get('description', ''),
        'active': data.get('active', True),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    result = offers_collection.insert_one(offer)
    offer['_id'] = str(result.inserted_id)
    return jsonify(serialize_doc(offer)), 201

@app.route('/api/offers/<offer_id>', methods=['PUT'])
@admin_required
def update_offer(offer_id):
    """
    Update Offer
    ---
    tags:
      - Offers
    summary: Update an existing offer
    description: Admin endpoint to update offer details
    security:
      - Bearer: []
    parameters:
      - in: path
        name: offer_id
        type: string
        required: true
        description: Offer ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            type:
              type: string
              enum: [percentage, fixed]
            value:
              type: number
            description:
              type: string
            active:
              type: boolean
    responses:
      200:
        description: Offer updated successfully
        schema:
          type: object
          properties:
            _id:
              type: string
            code:
              type: string
      400:
        description: Invalid offer type or ID
      404:
        description: Offer not found
      403:
        description: Admin access required
    """
    try:
        data = request.get_json()
        update_data = {'updated_at': datetime.utcnow()}
        
        if 'type' in data:
            if data['type'] not in ['percentage', 'fixed']:
                return jsonify({'message': 'Invalid offer type'}), 400
            update_data['type'] = data['type']
        if 'value' in data:
            update_data['value'] = float(data['value'])
        if 'description' in data:
            update_data['description'] = data['description']
        if 'active' in data:
            update_data['active'] = data['active']
        
        result = offers_collection.update_one(
            {'_id': ObjectId(offer_id)},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'message': 'Offer not found'}), 404
        
        offer = offers_collection.find_one({'_id': ObjectId(offer_id)})
        return jsonify(serialize_doc(offer)), 200
    except:
        return jsonify({'message': 'Invalid offer ID'}), 400

@app.route('/api/offers/<offer_id>', methods=['DELETE'])
@admin_required
def delete_offer(offer_id):
    """
    Delete Offer
    ---
    tags:
      - Offers
    summary: Delete an offer
    description: Admin endpoint to delete an offer code
    security:
      - Bearer: []
    parameters:
      - in: path
        name: offer_id
        type: string
        required: true
        description: Offer ID
    responses:
      200:
        description: Offer deleted successfully
      400:
        description: Invalid offer ID
      404:
        description: Offer not found
      403:
        description: Admin access required
    """
    try:
        result = offers_collection.delete_one({'_id': ObjectId(offer_id)})
        if result.deleted_count == 0:
            return jsonify({'message': 'Offer not found'}), 404
        return jsonify({'message': 'Offer deleted successfully'}), 200
    except:
        return jsonify({'message': 'Invalid offer ID'}), 400

# ==================== TESTIMONIALS ROUTES ====================

@app.route('/api/testimonials', methods=['GET'])
def get_testimonials():
    """
    Get Testimonials
    ---
    tags:
      - Testimonials
    summary: Get all testimonials
    description: Retrieve all customer testimonials/reviews. Only approved testimonials are returned by default.
    parameters:
      - in: query
        name: approved
        type: string
        required: false
        description: Filter by approval status (true/false). Default is true for public, false for admin.
        example: true
    responses:
      200:
        description: List of testimonials
        schema:
          type: array
          items:
            type: object
            properties:
              _id:
                type: string
              customer_name:
                type: string
              review:
                type: string
              rating:
                type: integer
              approved:
                type: boolean
              created_at:
                type: string
    """
    approved_only = request.args.get('approved', 'true').lower() == 'true'
    query = {'approved': True} if approved_only else {}
    testimonials = list(testimonials_collection.find(query).sort('created_at', -1))
    return jsonify([serialize_doc(t) for t in testimonials]), 200

@app.route('/api/testimonials', methods=['POST'])
def create_testimonial():
    """
    Create Testimonial
    ---
    tags:
      - Testimonials
    summary: Create a new testimonial
    description: Submit a new customer testimonial/review. Requires approval by admin before being displayed.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - customer_name
            - review
          properties:
            customer_name:
              type: string
              example: John Doe
            review:
              type: string
              example: Great service and fast delivery!
            rating:
              type: integer
              minimum: 1
              maximum: 5
              example: 5
    responses:
      201:
        description: Testimonial created successfully (pending approval)
        schema:
          type: object
          properties:
            _id:
              type: string
            customer_name:
              type: string
            review:
              type: string
            approved:
              type: boolean
      400:
        description: Missing required fields
    """
    data = request.get_json()
    required_fields = ['customer_name', 'review']
    
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields: customer_name, review'}), 400
    
    testimonial = {
        'customer_name': data['customer_name'],
        'review': data['review'],
        'rating': data.get('rating', 5),
        'approved': False,  # Requires admin approval
        'created_at': datetime.utcnow()
    }
    
    result = testimonials_collection.insert_one(testimonial)
    testimonial['_id'] = str(result.inserted_id)
    return jsonify(serialize_doc(testimonial)), 201

@app.route('/api/testimonials/<testimonial_id>', methods=['PUT'])
@admin_required
def update_testimonial(testimonial_id):
    """
    Update Testimonial
    ---
    tags:
      - Testimonials
    summary: Update testimonial (Admin only)
    description: Admin endpoint to update testimonial details or approve/reject testimonials
    security:
      - Bearer: []
    parameters:
      - in: path
        name: testimonial_id
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            customer_name:
              type: string
            review:
              type: string
            rating:
              type: integer
            approved:
              type: boolean
    responses:
      200:
        description: Testimonial updated successfully
      400:
        description: Invalid testimonial ID
      404:
        description: Testimonial not found
      403:
        description: Admin access required
    """
    try:
        data = request.get_json()
        update_data = {}
        
        if 'customer_name' in data:
            update_data['customer_name'] = data['customer_name']
        if 'review' in data:
            update_data['review'] = data['review']
        if 'rating' in data:
            update_data['rating'] = int(data['rating'])
        if 'approved' in data:
            update_data['approved'] = data['approved']
        
        if not update_data:
            return jsonify({'message': 'No fields to update'}), 400
        
        result = testimonials_collection.update_one(
            {'_id': ObjectId(testimonial_id)},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'message': 'Testimonial not found'}), 404
        
        testimonial = testimonials_collection.find_one({'_id': ObjectId(testimonial_id)})
        return jsonify(serialize_doc(testimonial)), 200
    except:
        return jsonify({'message': 'Invalid testimonial ID'}), 400

@app.route('/api/testimonials/<testimonial_id>', methods=['DELETE'])
@admin_required
def delete_testimonial(testimonial_id):
    """
    Delete Testimonial
    ---
    tags:
      - Testimonials
    summary: Delete testimonial (Admin only)
    description: Admin endpoint to delete a testimonial
    security:
      - Bearer: []
    parameters:
      - in: path
        name: testimonial_id
        type: string
        required: true
    responses:
      200:
        description: Testimonial deleted successfully
      400:
        description: Invalid testimonial ID
      404:
        description: Testimonial not found
      403:
        description: Admin access required
    """
    try:
        result = testimonials_collection.delete_one({'_id': ObjectId(testimonial_id)})
        if result.deleted_count == 0:
            return jsonify({'message': 'Testimonial not found'}), 404
        return jsonify({'message': 'Testimonial deleted successfully'}), 200
    except:
        return jsonify({'message': 'Invalid testimonial ID'}), 400

# ==================== CALLBACK REQUESTS ROUTES ====================

@app.route('/api/callback-requests', methods=['POST'])
def create_callback_request():
    """
    Create Callback Request
    ---
    tags:
      - Callback Requests
    summary: Submit a callback request
    description: Submit a request for pharmacy to call back the customer
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - phone
          properties:
            name:
              type: string
              example: John Doe
            phone:
              type: string
              example: +1234567890
            email:
              type: string
              example: john@example.com
            medicine:
              type: string
              example: Aspirin 100mg
            message:
              type: string
              example: Need consultation about this medicine
    responses:
      201:
        description: Callback request created successfully
        schema:
          type: object
          properties:
            _id:
              type: string
            name:
              type: string
            phone:
              type: string
            status:
              type: string
      400:
        description: Missing required fields
    """
    data = request.get_json()
    required_fields = ['name', 'phone']
    
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields: name, phone'}), 400
    
    callback_request = {
        'name': data['name'],
        'phone': data['phone'],
        'email': data.get('email', ''),
        'medicine': data.get('medicine', ''),
        'message': data.get('message', ''),
        'status': 'pending',
        'created_at': datetime.utcnow()
    }
    
    result = callback_requests_collection.insert_one(callback_request)
    callback_request['_id'] = str(result.inserted_id)
    return jsonify(serialize_doc(callback_request)), 201

@app.route('/api/callback-requests', methods=['GET'])
@admin_required
def get_callback_requests():
    """
    Get Callback Requests
    ---
    tags:
      - Callback Requests
    summary: Get all callback requests (Admin only)
    description: Admin endpoint to retrieve all callback requests
    security:
      - Bearer: []
    parameters:
      - in: query
        name: status
        type: string
        required: false
        description: Filter by status (pending, contacted, completed)
    responses:
      200:
        description: List of callback requests
        schema:
          type: array
          items:
            type: object
      403:
        description: Admin access required
    """
    status_filter = request.args.get('status', '')
    query = {}
    if status_filter:
        query = {'status': status_filter}
    
    requests = list(callback_requests_collection.find(query).sort('created_at', -1))
    return jsonify([serialize_doc(r) for r in requests]), 200

@app.route('/api/callback-requests/<request_id>', methods=['PUT'])
@admin_required
def update_callback_request(request_id):
    """
    Update Callback Request Status
    ---
    tags:
      - Callback Requests
    summary: Update callback request status (Admin only)
    description: Admin endpoint to update the status of a callback request
    security:
      - Bearer: []
    parameters:
      - in: path
        name: request_id
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            status:
              type: string
              enum: [pending, contacted, completed]
    responses:
      200:
        description: Request updated successfully
      400:
        description: Invalid status or request ID
      404:
        description: Request not found
      403:
        description: Admin access required
    """
    try:
        data = request.get_json()
        status = data.get('status')
        
        if status and status not in ['pending', 'contacted', 'completed']:
            return jsonify({'message': 'Invalid status'}), 400
        
        update_data = {}
        if 'status' in data:
            update_data['status'] = status
        
        if not update_data:
            return jsonify({'message': 'No fields to update'}), 400
        
        result = callback_requests_collection.update_one(
            {'_id': ObjectId(request_id)},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'message': 'Request not found'}), 404
        
        request_doc = callback_requests_collection.find_one({'_id': ObjectId(request_id)})
        return jsonify(serialize_doc(request_doc)), 200
    except:
        return jsonify({'message': 'Invalid request ID'}), 400

# ==================== DASHBOARD STATS ====================

@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """
    Get Dashboard Statistics
    ---
    tags:
      - Admin
    summary: Get admin dashboard statistics
    description: Retrieve statistics for the admin dashboard including total products, orders, revenue, and recent orders.
    security:
      - Bearer: []
    responses:
      200:
        description: Dashboard statistics
        schema:
          type: object
          properties:
            total_products:
              type: integer
              example: 50
            total_orders:
              type: integer
              example: 120
            pending_orders:
              type: integer
              example: 5
            total_revenue:
              type: number
              example: 12500.50
            recent_orders:
              type: array
              items:
                type: object
      401:
        description: Unauthorized - Invalid or missing token
      403:
        description: Forbidden - Admin access required
    """
    total_products = products_collection.count_documents({})
    total_orders = orders_collection.count_documents({})
    pending_orders = orders_collection.count_documents({'status': 'pending'})
    
    # Calculate total revenue
    pipeline = [
        {'$match': {'status': {'$ne': 'cancelled'}}},
        {'$group': {'_id': None, 'total': {'$sum': '$total'}}}
    ]
    revenue_result = list(orders_collection.aggregate(pipeline))
    total_revenue = revenue_result[0]['total'] if revenue_result else 0
    
    # Recent orders
    recent_orders = list(orders_collection.find({}).sort('created_at', -1).limit(5))
    
    return jsonify({
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'recent_orders': [serialize_doc(o) for o in recent_orders]
    }), 200

# Ensure database is connected before handling requests
@app.before_request
def ensure_db_connection():
    """Ensure MongoDB connection is established before handling requests."""
    try:
        get_db()
    except Exception as e:
        # Only fail if not in CI/testing environment
        if not (os.getenv('CI') or os.getenv('GITHUB_ACTIONS')):
            print(f"Database connection error: {e}")

if __name__ == '__main__':
    import sys
    # Initialize database and admin when running directly
    try:
        get_db()
        init_admin()
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")
        print("App will start but database operations will fail until MONGO_URI is configured.")
    
    # Get port from environment variable (for Deta Space, Render, Railway, etc.)
    port = int(os.getenv('PORT', 5000))
    # Disable reloader on Windows to avoid socket errors
    use_reloader = sys.platform != 'win32' and os.getenv('FLASK_ENV') == 'development'
    app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true', host='0.0.0.0', port=port, use_reloader=use_reloader)


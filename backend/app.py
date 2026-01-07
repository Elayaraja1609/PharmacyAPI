from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from functools import wraps
from flasgger import Swagger
import json

load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['JWT_ALGORITHM'] = 'HS256'

# CORS configuration - Allow all origins for development
# For production, specify exact origins
CORS(app, 
     resources={r"/api/*": {"origins": "*"}},
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     supports_credentials=True,
     expose_headers=["Content-Type", "Authorization"])

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

# MySQL connection - Lazy initialization to avoid connection during import (for CI/testing)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'pharmacy'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': int(os.getenv('DB_PORT', 3306)),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'autocommit': True
}

db_connection = None
db_cursor = None

def get_db():
    """Initialize MySQL connection lazily. This allows imports to succeed without MySQL connection."""
    global db_connection, db_cursor
    
    if db_connection is None or not db_connection.is_connected():
        try:
            db_connection = mysql.connector.connect(**DB_CONFIG)
            db_cursor = db_connection.cursor(dictionary=True, buffered=True)
            print("MySQL connection established successfully")
        except Error as e:
            # If connection fails during import (e.g., in CI), allow import to succeed
            if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
                print(f"Warning: MySQL connection skipped in CI environment: {e}")
            else:
                raise ConnectionError(f"MySQL connection failed: {e}")
    
    return db_connection

# Initialize admin user if not exists (only when actually running, not during import)
def init_admin():
    """Initialize admin user. Only runs when database is actually accessed."""
    try:
        get_db()  # Ensure database is connected
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'admin'")
        result = cursor.fetchone()
        
        if result and result['count'] == 0:
            cursor.execute(
                "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s)",
                ('admin', generate_password_hash('admin123'), 'admin@pharmacy.com', 'admin')
            )
            db_connection.commit()
            print("Default admin created: username='admin', password='admin123'")
        cursor.close()
    except (ConnectionError, Exception) as e:
        # Silently fail during import/testing - will be initialized when app actually runs
        if not (os.getenv('CI') or os.getenv('GITHUB_ACTIONS')):
            print(f"Warning: Could not initialize admin: {e}")

# Don't call init_admin() at import time - will be called when app starts

# Role-based access control decorators
def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()
            get_db()
            cursor = db_connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE id = %s", (current_user,))
            user = cursor.fetchone()
            cursor.close()
            
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
        get_db()
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        
        if not user or user.get('role') != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# ==================== CORS PREFLIGHT HANDLER ====================

@app.before_request
def handle_preflight():
    """Handle CORS preflight requests"""
    if request.method == "OPTIONS":
        response = jsonify({'status': 'ok'})
        origin = request.headers.get('Origin')
        if origin:
            response.headers.add("Access-Control-Allow-Origin", origin)
        else:
            response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-Requested-With")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
        response.headers.add('Access-Control-Allow-Credentials', "true")
        response.headers.add('Access-Control-Max-Age', "3600")
        return response, 200

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
    
    get_db()
    cursor = db_connection.cursor(dictionary=True)
    
    # Try to find user by username first (for admin)
    cursor.execute("SELECT * FROM users WHERE username = %s", (identifier,))
    user = cursor.fetchone()
    
    # If not found by username, try by phone (for customer)
    if not user:
        cursor.execute("SELECT * FROM users WHERE phone = %s", (identifier,))
        user = cursor.fetchone()
    
    cursor.close()
    
    if user and check_password_hash(user['password'], password):
        user_id = str(user['id'])
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
    get_db()
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    
    if user:
        response_data = {
            'user_id': str(user['id']),
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
    
    get_db()
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    
    if user and check_password_hash(user['password'], password):
        user_id = str(user['id'])
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
    get_db()
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    
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
    
    get_db()
    cursor = db_connection.cursor(dictionary=True)
    
    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE email = %s OR phone = %s", (data['email'], data['phone']))
    existing_user = cursor.fetchone()
    if existing_user:
        cursor.close()
        return jsonify({'message': 'Email or phone already exists'}), 400
    
    # Create user with default role 'customer'
    cursor.execute(
        "INSERT INTO users (name, email, phone, password, address, role) VALUES (%s, %s, %s, %s, %s, %s)",
        (data['name'], data['email'], data['phone'], generate_password_hash(data['password']), 
         data.get('address', ''), 'customer')
    )
    user_id = cursor.lastrowid
    db_connection.commit()
    cursor.close()
    
    # Create access token
    access_token = create_access_token(identity=str(user_id))
    
    return jsonify({
        'message': 'User registered successfully',
        'user_id': str(user_id),
        'access_token': access_token,
        'name': data['name'],
        'email': data['email'],
        'phone': data['phone'],
        'role': 'customer'
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
    
    get_db()
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE phone = %s AND role = 'customer'", (phone,))
    user = cursor.fetchone()
    cursor.close()
    
    if user and check_password_hash(user['password'], password):
        user_id = str(user['id'])
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
    get_db()
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    
    if user:
        return jsonify({
            'customer_id': str(user['id']),
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
    
    get_db()
    cursor = db_connection.cursor(dictionary=True)
    
    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE username = %s", (data['username'],))
    existing_user = cursor.fetchone()
    if existing_user:
        cursor.close()
        return jsonify({'message': 'Username already exists'}), 400
    
    cursor.execute(
        "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s)",
        (data['username'], generate_password_hash(data['password']), data.get('email', ''), data['role'])
    )
    user_id = cursor.lastrowid
    db_connection.commit()
    
    cursor.execute("SELECT id, username, email, role, created_at FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    
    user['id'] = str(user['id'])
    return jsonify(user), 201

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
    get_db()
    cursor = db_connection.cursor(dictionary=True)
    
    if role_filter:
        cursor.execute("SELECT id, username, email, role, created_at FROM users WHERE role = %s ORDER BY username", (role_filter,))
    else:
        cursor.execute("SELECT id, username, email, role, created_at FROM users ORDER BY username")
    
    users = cursor.fetchall()
    cursor.close()
    
    # Convert id to string
    for user in users:
        user['id'] = str(user['id'])
    
    return jsonify(users), 200

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
        updates = []
        params = []
        
        if 'password' in data:
            updates.append("password = %s")
            params.append(generate_password_hash(data['password']))
        if 'email' in data:
            updates.append("email = %s")
            params.append(data['email'])
        if 'role' in data:
            if data['role'] not in ['admin', 'driver', 'helper']:
                return jsonify({'message': 'Invalid role'}), 400
            updates.append("role = %s")
            params.append(data['role'])
        
        if not updates:
            return jsonify({'message': 'No fields to update'}), 400
        
        params.append(user_id)
        get_db()
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = %s", params)
        db_connection.commit()
        
        if cursor.rowcount == 0:
            cursor.close()
            return jsonify({'message': 'User not found'}), 404
        
        cursor.execute("SELECT id, username, email, role, created_at FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        
        user['id'] = str(user['id'])
        return jsonify(user), 200
    except Exception as e:
        return jsonify({'message': f'Invalid user ID: {str(e)}'}), 400

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
    try:
        get_db()
        cursor = db_connection.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        db_connection.commit()
        
        if cursor.rowcount == 0:
            cursor.close()
            return jsonify({'message': 'User not found'}), 404
        
        cursor.close()
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        return jsonify({'message': f'Invalid user ID: {str(e)}'}), 400

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
        get_db()
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        cursor.close()
        
        if product:
            product['id'] = str(product['id'])
            return jsonify(product), 200
        return jsonify({'message': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'message': f'Invalid product ID: {str(e)}'}), 400

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
    
    get_db()
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO products (name, description, price, stock, category, image) VALUES (%s, %s, %s, %s, %s, %s)",
        (data['name'], data.get('description', ''), float(data['price']), int(data['stock']), 
         data.get('category', 'General'), data.get('image', ''))
    )
    product_id = cursor.lastrowid
    db_connection.commit()
    
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    
    product['id'] = str(product['id'])
    return jsonify(product), 201

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
        updates = []
        params = []
        
        if 'name' in data:
            updates.append("name = %s")
            params.append(data['name'])
        if 'description' in data:
            updates.append("description = %s")
            params.append(data['description'])
        if 'price' in data:
            updates.append("price = %s")
            params.append(float(data['price']))
        if 'stock' in data:
            updates.append("stock = %s")
            params.append(int(data['stock']))
        if 'category' in data:
            updates.append("category = %s")
            params.append(data['category'])
        if 'image' in data:
            updates.append("image = %s")
            params.append(data['image'])
        
        if not updates:
            return jsonify({'message': 'No fields to update'}), 400
        
        params.append(product_id)
        get_db()
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute(f"UPDATE products SET {', '.join(updates)} WHERE id = %s", params)
        db_connection.commit()
        
        if cursor.rowcount == 0:
            cursor.close()
            return jsonify({'message': 'Product not found'}), 404
        
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        cursor.close()
        
        product['id'] = str(product['id'])
        return jsonify(product), 200
    except Exception as e:
        return jsonify({'message': f'Invalid product ID: {str(e)}'}), 400

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
        get_db()
        cursor = db_connection.cursor()
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        db_connection.commit()
        
        if cursor.rowcount == 0:
            cursor.close()
            return jsonify({'message': 'Product not found'}), 404
        
        cursor.close()
        return jsonify({'message': 'Product deleted successfully'}), 200
    except Exception as e:
        return jsonify({'message': f'Invalid product ID: {str(e)}'}), 400

# ==================== PRODUCT ROUTES (LIST) ====================

@app.route('/api/products', methods=['GET'])
def get_products():
    """
    Get Products
    ---
    tags:
      - Products
    summary: Get all products
    description: Retrieve all products. Supports search filtering.
    parameters:
      - in: query
        name: search
        type: string
        required: false
        description: Search products by name, description, or category
    responses:
      200:
        description: List of products
    """
    search = request.args.get('search', '')
    get_db()
    cursor = db_connection.cursor(dictionary=True)
    
    if search:
        cursor.execute(
            "SELECT * FROM products WHERE name LIKE %s OR description LIKE %s OR category LIKE %s ORDER BY name",
            (f'%{search}%', f'%{search}%', f'%{search}%')
        )
    else:
        cursor.execute("SELECT * FROM products ORDER BY name")
    
    products = cursor.fetchall()
    cursor.close()
    
    # Convert id to string
    for product in products:
        product['id'] = str(product['id'])
    
    return jsonify(products), 200

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
    
    get_db()
    cursor = db_connection.cursor(dictionary=True)
    
    if offer_code:
        cursor.execute("SELECT * FROM offers WHERE code = %s AND active = TRUE", (offer_code,))
        offer = cursor.fetchone()
        if offer:
            if offer['type'] == 'percentage':
                discount = final_total * (float(offer['value']) / 100)
            else:
                discount = float(offer['value'])
            final_total = max(0, final_total - discount)
    
    # Insert order
    cursor.execute(
        "INSERT INTO orders (customer_name, customer_phone, customer_address, items, subtotal, discount, total, offer_code, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (customer['name'], customer['phone'], customer['address'], json.dumps(data['items']), 
         float(data['total']), discount, final_total, offer_code if offer_code else None, 'pending')
    )
    order_id = cursor.lastrowid
    db_connection.commit()
    
    # Update product stock
    for item in data['items']:
        cursor.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (item['quantity'], item['product_id']))
    db_connection.commit()
    
    # Fetch created order
    cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    order = cursor.fetchone()
    cursor.close()
    
    # Format response
    order['id'] = str(order['id'])
    order['items'] = json.loads(order['items'])
    order['customer'] = {
        'name': order['customer_name'],
        'phone': order['customer_phone'],
        'address': order['customer_address']
    }
    # Remove individual customer fields
    order.pop('customer_name', None)
    order.pop('customer_phone', None)
    order.pop('customer_address', None)
    
    return jsonify(order), 201

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
    get_db()
    cursor = db_connection.cursor(dictionary=True)
    
    if phone:
        cursor.execute("SELECT * FROM orders WHERE customer_phone = %s ORDER BY created_at DESC", (phone,))
    else:
        cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
    
    orders = cursor.fetchall()
    cursor.close()
    
    # Format orders for response
    formatted_orders = []
    for order in orders:
        order['id'] = str(order['id'])
        order['items'] = json.loads(order['items'])
        order['customer'] = {
            'name': order['customer_name'],
            'phone': order['customer_phone'],
            'address': order['customer_address']
        }
        order.pop('customer_name', None)
        order.pop('customer_phone', None)
        order.pop('customer_address', None)
        formatted_orders.append(order)
    
    return jsonify(formatted_orders), 200

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
        get_db()
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        order = cursor.fetchone()
        cursor.close()
        
        if order:
            order['id'] = str(order['id'])
            order['items'] = json.loads(order['items'])
            order['customer'] = {
                'name': order['customer_name'],
                'phone': order['customer_phone'],
                'address': order['customer_address']
            }
            order.pop('customer_name', None)
            order.pop('customer_phone', None)
            order.pop('customer_address', None)
            return jsonify(order), 200
        return jsonify({'message': 'Order not found'}), 404
    except Exception as e:
        return jsonify({'message': f'Invalid order ID: {str(e)}'}), 400

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
        
        get_db()
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("UPDATE orders SET status = %s WHERE id = %s", (status, order_id))
        db_connection.commit()
        
        if cursor.rowcount == 0:
            cursor.close()
            return jsonify({'message': 'Order not found'}), 404
        
        cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        order = cursor.fetchone()
        cursor.close()
        
        order['id'] = str(order['id'])
        order['items'] = json.loads(order['items'])
        order['customer'] = {
            'name': order['customer_name'],
            'phone': order['customer_phone'],
            'address': order['customer_address']
        }
        order.pop('customer_name', None)
        order.pop('customer_phone', None)
        order.pop('customer_address', None)
        
        return jsonify(order), 200
    except Exception as e:
        return jsonify({'message': f'Invalid order ID: {str(e)}'}), 400

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
    get_db()
    cursor = db_connection.cursor(dictionary=True)
    
    if active_only:
        cursor.execute("SELECT * FROM offers WHERE active = TRUE ORDER BY created_at DESC")
    else:
        cursor.execute("SELECT * FROM offers ORDER BY created_at DESC")
    
    offers = cursor.fetchall()
    cursor.close()
    
    for offer in offers:
        offer['id'] = str(offer['id'])
    
    return jsonify(offers), 200

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
    get_db()
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM offers WHERE code = %s AND active = TRUE", (offer_code,))
    offer = cursor.fetchone()
    cursor.close()
    
    if offer:
        offer['id'] = str(offer['id'])
        return jsonify(offer), 200
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
    
    get_db()
    cursor = db_connection.cursor(dictionary=True)
    
    # Check if code already exists
    cursor.execute("SELECT * FROM offers WHERE code = %s", (data['code'].upper(),))
    existing = cursor.fetchone()
    if existing:
        cursor.close()
        return jsonify({'message': 'Offer code already exists'}), 400
    
    cursor.execute(
        "INSERT INTO offers (code, type, value, description, active) VALUES (%s, %s, %s, %s, %s)",
        (data['code'].upper(), data['type'], float(data['value']), data.get('description', ''), data.get('active', True))
    )
    offer_id = cursor.lastrowid
    db_connection.commit()
    
    cursor.execute("SELECT * FROM offers WHERE id = %s", (offer_id,))
    offer = cursor.fetchone()
    cursor.close()
    
    offer['id'] = str(offer['id'])
    return jsonify(offer), 201

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
        updates = []
        params = []
        
        if 'type' in data:
            if data['type'] not in ['percentage', 'fixed']:
                return jsonify({'message': 'Invalid offer type'}), 400
            updates.append("type = %s")
            params.append(data['type'])
        if 'value' in data:
            updates.append("value = %s")
            params.append(float(data['value']))
        if 'description' in data:
            updates.append("description = %s")
            params.append(data['description'])
        if 'active' in data:
            updates.append("active = %s")
            params.append(data['active'])
        
        if not updates:
            return jsonify({'message': 'No fields to update'}), 400
        
        params.append(offer_id)
        get_db()
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute(f"UPDATE offers SET {', '.join(updates)} WHERE id = %s", params)
        db_connection.commit()
        
        if cursor.rowcount == 0:
            cursor.close()
            return jsonify({'message': 'Offer not found'}), 404
        
        cursor.execute("SELECT * FROM offers WHERE id = %s", (offer_id,))
        offer = cursor.fetchone()
        cursor.close()
        
        offer['id'] = str(offer['id'])
        return jsonify(offer), 200
    except Exception as e:
        return jsonify({'message': f'Invalid offer ID: {str(e)}'}), 400

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
        get_db()
        cursor = db_connection.cursor()
        cursor.execute("DELETE FROM offers WHERE id = %s", (offer_id,))
        db_connection.commit()
        
        if cursor.rowcount == 0:
            cursor.close()
            return jsonify({'message': 'Offer not found'}), 404
        
        cursor.close()
        return jsonify({'message': 'Offer deleted successfully'}), 200
    except Exception as e:
        return jsonify({'message': f'Invalid offer ID: {str(e)}'}), 400

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
    get_db()
    cursor = db_connection.cursor(dictionary=True)
    
    if approved_only:
        cursor.execute("SELECT * FROM testimonials WHERE approved = TRUE ORDER BY created_at DESC")
    else:
        cursor.execute("SELECT * FROM testimonials ORDER BY created_at DESC")
    
    testimonials = cursor.fetchall()
    cursor.close()
    
    for testimonial in testimonials:
        testimonial['id'] = str(testimonial['id'])
    
    return jsonify(testimonials), 200

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
    
    get_db()
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO testimonials (customer_name, review, rating, approved) VALUES (%s, %s, %s, %s)",
        (data['customer_name'], data['review'], data.get('rating', 5), False)
    )
    testimonial_id = cursor.lastrowid
    db_connection.commit()
    
    cursor.execute("SELECT * FROM testimonials WHERE id = %s", (testimonial_id,))
    testimonial = cursor.fetchone()
    cursor.close()
    
    testimonial['id'] = str(testimonial['id'])
    return jsonify(testimonial), 201

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
        updates = []
        params = []
        
        if 'customer_name' in data:
            updates.append("customer_name = %s")
            params.append(data['customer_name'])
        if 'review' in data:
            updates.append("review = %s")
            params.append(data['review'])
        if 'rating' in data:
            updates.append("rating = %s")
            params.append(int(data['rating']))
        if 'approved' in data:
            updates.append("approved = %s")
            params.append(data['approved'])
        
        if not updates:
            return jsonify({'message': 'No fields to update'}), 400
        
        params.append(testimonial_id)
        get_db()
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute(f"UPDATE testimonials SET {', '.join(updates)} WHERE id = %s", params)
        db_connection.commit()
        
        if cursor.rowcount == 0:
            cursor.close()
            return jsonify({'message': 'Testimonial not found'}), 404
        
        cursor.execute("SELECT * FROM testimonials WHERE id = %s", (testimonial_id,))
        testimonial = cursor.fetchone()
        cursor.close()
        
        testimonial['id'] = str(testimonial['id'])
        return jsonify(testimonial), 200
    except Exception as e:
        return jsonify({'message': f'Invalid testimonial ID: {str(e)}'}), 400

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
        get_db()
        cursor = db_connection.cursor()
        cursor.execute("DELETE FROM testimonials WHERE id = %s", (testimonial_id,))
        db_connection.commit()
        
        if cursor.rowcount == 0:
            cursor.close()
            return jsonify({'message': 'Testimonial not found'}), 404
        
        cursor.close()
        return jsonify({'message': 'Testimonial deleted successfully'}), 200
    except Exception as e:
        return jsonify({'message': f'Invalid testimonial ID: {str(e)}'}), 400

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
    
    get_db()
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO callback_requests (name, phone, email, medicine, message, status) VALUES (%s, %s, %s, %s, %s, %s)",
        (data['name'], data['phone'], data.get('email', ''), data.get('medicine', ''), 
         data.get('message', ''), 'pending')
    )
    request_id = cursor.lastrowid
    db_connection.commit()
    
    cursor.execute("SELECT * FROM callback_requests WHERE id = %s", (request_id,))
    callback_request = cursor.fetchone()
    cursor.close()
    
    callback_request['id'] = str(callback_request['id'])
    return jsonify(callback_request), 201

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
    get_db()
    cursor = db_connection.cursor(dictionary=True)
    
    if status_filter:
        cursor.execute("SELECT * FROM callback_requests WHERE status = %s ORDER BY created_at DESC", (status_filter,))
    else:
        cursor.execute("SELECT * FROM callback_requests ORDER BY created_at DESC")
    
    requests = cursor.fetchall()
    cursor.close()
    
    for req in requests:
        req['id'] = str(req['id'])
    
    return jsonify(requests), 200

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
        
        if not status:
            return jsonify({'message': 'No fields to update'}), 400
        
        get_db()
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("UPDATE callback_requests SET status = %s WHERE id = %s", (status, request_id))
        db_connection.commit()
        
        if cursor.rowcount == 0:
            cursor.close()
            return jsonify({'message': 'Request not found'}), 404
        
        cursor.execute("SELECT * FROM callback_requests WHERE id = %s", (request_id,))
        request_doc = cursor.fetchone()
        cursor.close()
        
        request_doc['id'] = str(request_doc['id'])
        return jsonify(request_doc), 200
    except Exception as e:
        return jsonify({'message': f'Invalid request ID: {str(e)}'}), 400

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
    get_db()
    cursor = db_connection.cursor(dictionary=True)
    
    cursor.execute("SELECT COUNT(*) as count FROM products")
    total_products = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM orders")
    total_orders = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM orders WHERE status = 'pending'")
    pending_orders = cursor.fetchone()['count']
    
    cursor.execute("SELECT SUM(total) as total FROM orders WHERE status != 'cancelled'")
    revenue_result = cursor.fetchone()
    total_revenue = float(revenue_result['total']) if revenue_result['total'] else 0
    
    cursor.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 5")
    recent_orders = cursor.fetchall()
    cursor.close()
    
    # Format recent orders
    formatted_orders = []
    for order in recent_orders:
        order['id'] = str(order['id'])
        order['items'] = json.loads(order['items'])
        order['customer'] = {
            'name': order['customer_name'],
            'phone': order['customer_phone'],
            'address': order['customer_address']
        }
        order.pop('customer_name', None)
        order.pop('customer_phone', None)
        order.pop('customer_address', None)
        formatted_orders.append(order)
    
    return jsonify({
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'recent_orders': formatted_orders
    }), 200

# Ensure database is connected before handling requests (skip for OPTIONS)
@app.before_request
def ensure_db_connection():
    """Ensure MySQL connection is established before handling requests."""
    # Skip database connection for OPTIONS requests
    if request.method == "OPTIONS":
        return
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
        print("App will start but database operations will fail until MySQL connection is configured.")
    
    # Get port from environment variable (for Deta Space, Render, Railway, etc.)
    port = int(os.getenv('PORT', 5000))
    # Disable reloader on Windows to avoid socket errors
    use_reloader = sys.platform != 'win32' and os.getenv('FLASK_ENV') == 'development'
    app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true', host='0.0.0.0', port=port, use_reloader=use_reloader)


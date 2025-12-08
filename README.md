# Pharmacy API - Backend

Flask REST API backend for a local pharmacy shop management system.

## Tech Stack

- **Python 3.9+**
- **Flask** - Web framework
- **MongoDB Atlas** - Database
- **JWT Authentication** - Secure admin access
- **Flask-CORS** - Cross-origin resource sharing
- **Flask-JWT-Extended** - JWT token management
- **Flasgger** - Swagger/OpenAPI documentation
- **PyMongo** - MongoDB driver

## Features

### API Endpoints
- ✅ Products CRUD operations
- ✅ Orders management
- ✅ Offer codes system
- ✅ Admin authentication (JWT)
- ✅ User management (admin, driver, helper roles)
- ✅ Testimonials management
- ✅ Callback requests handling
- ✅ Dashboard statistics
- ✅ Swagger/OpenAPI documentation

### Security
- ✅ JWT-based authentication
- ✅ Role-based access control
- ✅ Password hashing (Werkzeug)
- ✅ CORS configuration

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Elayaraja1609/PharmacyAPI.git
cd PharmacyAPI
```

### 2. Set Up Virtual Environment

```bash
cd backend
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/pharmacy?retryWrites=true&w=majority
JWT_SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
```

### 5. Run the Server

```bash
python app.py
```

The API will be available at: `http://localhost:5000`

**Swagger Documentation**: `http://localhost:5000/api-docs`

## Default Admin Credentials

- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Change these credentials in production!**

## API Documentation

### Swagger UI

Access interactive API documentation at:
```
http://localhost:5000/api-docs
```

### Main Endpoints

#### Authentication
- `POST /api/admin/login` - Admin login
- `GET /api/admin/verify` - Verify JWT token

#### Products
- `GET /api/products` - Get all products (supports ?search= query)
- `GET /api/products/<id>` - Get single product
- `POST /api/products` - Create product (Admin only)
- `PUT /api/products/<id>` - Update product (Admin only)
- `DELETE /api/products/<id>` - Delete product (Admin only)

#### Orders
- `GET /api/orders` - Get all orders (supports ?phone= query)
- `GET /api/orders/<id>` - Get single order
- `POST /api/orders` - Create new order
- `PUT /api/orders/<id>` - Update order status (Admin only)

#### Offers
- `GET /api/offers` - Get all offers (supports ?active=true/false)
- `GET /api/offers/<code>` - Get offer by code
- `POST /api/offers` - Create offer (Admin only)
- `PUT /api/offers/<id>` - Update offer (Admin only)
- `DELETE /api/offers/<id>` - Delete offer (Admin only)

#### Users
- `GET /api/users` - Get all users (Admin only)
- `GET /api/users/<id>` - Get single user (Admin only)
- `POST /api/users` - Create user (Admin only)
- `PUT /api/users/<id>` - Update user (Admin only)
- `DELETE /api/users/<id>` - Delete user (Admin only)

#### Testimonials
- `GET /api/testimonials` - Get all testimonials
- `POST /api/testimonials` - Create testimonial (Admin only)
- `PUT /api/testimonials/<id>` - Update testimonial (Admin only)
- `DELETE /api/testimonials/<id>` - Delete testimonial (Admin only)

#### Callback Requests
- `GET /api/callback-requests` - Get all callback requests (Admin only)
- `POST /api/callback-requests` - Submit callback request
- `PUT /api/callback-requests/<id>` - Update callback request status (Admin only)

#### Dashboard
- `GET /api/admin/stats` - Get dashboard statistics (Admin only)

## Project Structure

```
backend/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # For Heroku/Render deployment
├── Spacefile             # For Deta Space deployment
├── .env.example          # Environment variables template
├── .detaignore           # Deta Space ignore file
├── SWAGGER_GUIDE.md      # Swagger documentation guide
├── DETA_DEPLOYMENT.md    # Deta Space deployment guide
└── ALTERNATIVE_DEPLOYMENT.md  # Alternative deployment options
```

## Deployment

### Option 1: Render (Recommended)

See `RENDER_CI_CD_QUICKSTART.md` for detailed instructions.

**Quick Steps:**
1. Sign up at [Render](https://render.com)
2. Create new Web Service
3. Connect GitHub repository
4. Set root directory: `backend`
5. Build command: `pip install -r requirements.txt`
6. Start command: `python app.py`
7. Add environment variables

### Option 2: Railway

1. Sign up at [Railway](https://railway.app)
2. Create new project from GitHub
3. Add environment variables
4. Deploy!

### Option 3: Deta Space

See `backend/DETA_DEPLOYMENT.md` for detailed instructions.

### CI/CD Setup

See `CI_CD_GUIDE.md` for GitHub Actions CI/CD setup.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MONGO_URI` | MongoDB Atlas connection string | Yes |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | Yes |
| `FLASK_ENV` | Flask environment (development/production) | No |
| `FLASK_DEBUG` | Enable debug mode (True/False) | No |
| `PORT` | Server port (default: 5000) | No |

## MongoDB Setup

1. Create account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster (M0 tier)
3. Create database user
4. Whitelist IP addresses (use `0.0.0.0/0` for all IPs)
5. Get connection string
6. Update `MONGO_URI` in `.env`

## Development

### Running in Development Mode

```bash
python app.py
```

The server runs on `http://localhost:5000` with auto-reload disabled on Windows.

### Testing Endpoints

Use Swagger UI at `http://localhost:5000/api-docs` or tools like:
- Postman
- cURL
- HTTPie

### Example API Call

```bash
# Get all products
curl http://localhost:5000/api/products

# Admin login
curl -X POST http://localhost:5000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

## Security Notes

1. **Change default admin credentials** in production
2. **Use strong JWT_SECRET_KEY** (random, long string)
3. **Enable HTTPS** in production
4. **Configure CORS** properly for your frontend domain
5. **Never commit `.env` file** to version control

## License

This project is open source and available for use.

## Support

For issues or questions, please check:
- `SWAGGER_GUIDE.md` - API documentation guide
- `CI_CD_GUIDE.md` - Deployment and CI/CD guide
- `RENDER_SECRETS_SETUP.md` - Render secrets setup

# Project Folder Structure

Complete folder structure for the Local Pharmacy application.

```
Pharmecy/
│
├── backend/                          # Flask Backend
│   ├── app.py                        # Main Flask application with all routes
│   ├── requirements.txt              # Python dependencies
│   ├── Procfile                      # Deployment configuration for Render/Railway
│   └── .env                          # Environment variables (create from .env.example)
│
├── frontend/                          # React Frontend
│   ├── public/                       # Static files
│   │   ├── robots.txt                # SEO robots file
│   │   └── sitemap.xml                # SEO sitemap
│   │
│   ├── src/                          # Source code
│   │   ├── components/               # Reusable React components
│   │   │   ├── Navbar.jsx            # Navigation bar component
│   │   │   └── Footer.jsx            # Footer component
│   │   │
│   │   ├── context/                  # React Context providers
│   │   │   ├── AuthContext.jsx       # Authentication context (admin login)
│   │   │   └── CartContext.jsx       # Shopping cart context
│   │   │
│   │   ├── pages/                    # Page components
│   │   │   ├── admin/                # Admin dashboard pages
│   │   │   │   ├── AdminDashboard.jsx    # Dashboard overview
│   │   │   │   ├── AdminLogin.jsx         # Admin login page
│   │   │   │   ├── AdminProducts.jsx      # Product management
│   │   │   │   ├── AdminOrders.jsx       # Order management
│   │   │   │   └── AdminOffers.jsx        # Offer code management
│   │   │   │
│   │   │   ├── Home.jsx              # Home page
│   │   │   ├── Products.jsx          # Products listing page
│   │   │   ├── Cart.jsx              # Shopping cart page
│   │   │   ├── Checkout.jsx          # Checkout page
│   │   │   └── OrderHistory.jsx      # Order history page
│   │   │
│   │   ├── services/                 # API services
│   │   │   └── api.js                # Axios API client configuration
│   │   │
│   │   ├── App.jsx                   # Main app component with routing
│   │   ├── main.jsx                  # React entry point
│   │   └── index.css                 # Global styles and Tailwind imports
│   │
│   ├── index.html                    # HTML template
│   ├── package.json                  # Node.js dependencies and scripts
│   ├── vite.config.js                # Vite configuration
│   ├── tailwind.config.js            # TailwindCSS configuration
│   ├── postcss.config.js             # PostCSS configuration
│   └── .env                          # Environment variables (create from .env.example)
│
├── README.md                         # Main project documentation
├── SETUP.md                          # Local setup instructions
├── DEPLOYMENT.md                     # Production deployment guide
└── FOLDER_STRUCTURE.md               # This file
```

## File Descriptions

### Backend Files

- **app.py**: Contains all Flask routes, MongoDB models, JWT authentication, and business logic
- **requirements.txt**: Python package dependencies
- **Procfile**: Used by Render/Railway for deployment
- **.env**: Environment variables (MongoDB URI, JWT secret, etc.)

### Frontend Files

#### Components
- **Navbar.jsx**: Navigation bar with cart count and admin links
- **Footer.jsx**: Footer with links and contact information

#### Contexts
- **AuthContext.jsx**: Manages admin authentication state and JWT tokens
- **CartContext.jsx**: Manages shopping cart state (localStorage persistence)

#### Pages - User Side
- **Home.jsx**: Landing page with pharmacy info, about us, and services
- **Products.jsx**: Product listing with search functionality
- **Cart.jsx**: Shopping cart with quantity management
- **Checkout.jsx**: Checkout form with customer details and offer code application
- **OrderHistory.jsx**: Order lookup by phone number

#### Pages - Admin Side
- **AdminLogin.jsx**: Admin authentication page
- **AdminDashboard.jsx**: Dashboard with statistics and recent orders
- **AdminProducts.jsx**: CRUD operations for products
- **AdminOrders.jsx**: View and manage all orders
- **AdminOffers.jsx**: CRUD operations for offer codes

#### Services
- **api.js**: Axios instance configured with base URL and JWT token interceptor

#### Configuration
- **vite.config.js**: Vite build tool configuration
- **tailwind.config.js**: TailwindCSS customization
- **postcss.config.js**: PostCSS plugins (Tailwind, Autoprefixer)
- **package.json**: Dependencies and npm scripts

### Public Files
- **robots.txt**: Search engine crawler instructions
- **sitemap.xml**: XML sitemap for SEO

## Key Technologies

### Backend
- Flask: Web framework
- PyMongo: MongoDB driver
- Flask-JWT-Extended: JWT authentication
- Flask-CORS: Cross-origin resource sharing
- python-dotenv: Environment variable management

### Frontend
- React 18: UI library
- React Router v6: Client-side routing
- Axios: HTTP client
- TailwindCSS: Utility-first CSS framework
- React Helmet Async: SEO meta tag management
- Vite: Build tool and dev server

## Database Collections

MongoDB collections (created automatically):
- **products**: Product catalog
- **orders**: Customer orders
- **offers**: Promotional codes
- **admin**: Admin user accounts

## Environment Variables

### Backend (.env)
```
MONGO_URI=mongodb+srv://...
JWT_SECRET_KEY=your-secret-key
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
HOST=0.0.0.0
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:5000/api
```

## API Endpoints

### Public Endpoints
- `GET /api/products` - List products (with search)
- `GET /api/products/:id` - Get single product
- `GET /api/orders?phone=...` - Get orders by phone
- `GET /api/orders/:id` - Get single order
- `POST /api/orders` - Create new order
- `GET /api/offers` - List offers
- `GET /api/offers/:code` - Get offer by code

### Admin Endpoints (JWT Required)
- `POST /api/admin/login` - Admin login
- `GET /api/admin/verify` - Verify token
- `GET /api/admin/stats` - Dashboard statistics
- `POST /api/products` - Create product
- `PUT /api/products/:id` - Update product
- `DELETE /api/products/:id` - Delete product
- `PUT /api/orders/:id` - Update order status
- `POST /api/offers` - Create offer
- `PUT /api/offers/:id` - Update offer
- `DELETE /api/offers/:id` - Delete offer


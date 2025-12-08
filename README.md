# Local Pharmacy - Full Stack Web Application

A complete full-stack web application for a local pharmacy shop with user-facing website and admin dashboard.

## Tech Stack

### Frontend
- React 18
- React Router v6
- Axios
- TailwindCSS
- React Helmet Async (SEO)
- Vite

### Backend
- Python 3.8+
- Flask
- MongoDB Atlas
- JWT Authentication
- Flask-CORS
- Flask-JWT-Extended

## Features

### User Side
- ✅ Home page with pharmacy details, about us, services
- ✅ Products list page with search functionality
- ✅ Shopping cart system
- ✅ Checkout page with customer details form
- ✅ Order history (search by phone number)
- ✅ Apply offer codes
- ✅ Fully mobile responsive
- ✅ SEO-friendly (robots.txt, sitemap.xml, meta tags)

### Admin Side
- ✅ JWT-protected admin login
- ✅ Dashboard overview with statistics
- ✅ Add/Edit/Delete products
- ✅ View and manage all orders
- ✅ Create/Edit/Delete offer codes
- ✅ Order status management

## Project Structure

```
Pharmecy/
├── backend/
│   ├── app.py                 # Flask application
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment variables example
├── frontend/
│   ├── public/
│   │   ├── robots.txt         # SEO robots file
│   │   └── sitemap.xml        # SEO sitemap
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── context/           # React contexts (Cart, Auth)
│   │   ├── pages/             # Page components
│   │   │   ├── admin/         # Admin pages
│   │   │   └── ...            # User pages
│   │   ├── services/          # API service
│   │   ├── App.jsx            # Main app component
│   │   └── main.jsx           # Entry point
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── .env.example
└── README.md
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up MongoDB Atlas:
   - Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Create a new cluster
   - Get your connection string
   - Update `.env` file with your MongoDB URI

5. Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

6. Update `.env` with your values:
```
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/pharmacy?retryWrites=true&w=majority
JWT_SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=True
```

7. Run the Flask server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

**Default Admin Credentials:**
- Username: `admin`
- Password: `admin123`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

4. Update `.env` with your API URL:
```
VITE_API_URL=http://localhost:5000/api
```

5. Run the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

6. Build for production:
```bash
npm run build
```

## API Endpoints

### Authentication
- `POST /api/admin/login` - Admin login
- `GET /api/admin/verify` - Verify JWT token

### Products
- `GET /api/products` - Get all products (supports ?search= query)
- `GET /api/products/<id>` - Get single product
- `POST /api/products` - Create product (Admin only)
- `PUT /api/products/<id>` - Update product (Admin only)
- `DELETE /api/products/<id>` - Delete product (Admin only)

### Orders
- `GET /api/orders` - Get all orders (supports ?phone= query)
- `GET /api/orders/<id>` - Get single order
- `POST /api/orders` - Create new order
- `PUT /api/orders/<id>` - Update order status (Admin only)

### Offers
- `GET /api/offers` - Get all offers (supports ?active=true/false)
- `GET /api/offers/<code>` - Get offer by code
- `POST /api/offers` - Create offer (Admin only)
- `PUT /api/offers/<id>` - Update offer (Admin only)
- `DELETE /api/offers/<id>` - Delete offer (Admin only)

### Dashboard
- `GET /api/admin/stats` - Get dashboard statistics (Admin only)

## Deployment

### Frontend Deployment (Netlify)

1. Build the frontend:
```bash
cd frontend
npm run build
```

2. Deploy to Netlify:
   - Sign up/login to [Netlify](https://www.netlify.com)
   - Drag and drop the `dist` folder, OR
   - Connect your Git repository
   - Set build command: `npm run build`
   - Set publish directory: `dist`
   - Add environment variable: `VITE_API_URL=https://your-backend-url.com/api`

3. Update `robots.txt` and `sitemap.xml` with your actual domain URL

### Backend Deployment (Render/Railway)

#### Using Render:

1. Sign up/login to [Render](https://render.com)
2. Create a new Web Service
3. Connect your Git repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python app.py`
6. Add environment variables:
   - `MONGO_URI`
   - `JWT_SECRET_KEY`
   - `FLASK_ENV=production`
   - `FLASK_DEBUG=False`

#### Using Railway:

1. Sign up/login to [Railway](https://railway.app)
2. Create a new project
3. Add a new service from GitHub
4. Add environment variables in the Variables tab
5. Railway will automatically detect Python and install dependencies

### Important Notes for Deployment

1. **CORS**: The backend is configured to allow CORS. Update `CORS(app)` in `app.py` if needed for production.

2. **MongoDB Atlas**: 
   - Whitelist your deployment server IP (or use 0.0.0.0/0 for all IPs in development)
   - Ensure your database user has read/write permissions

3. **JWT Secret**: Use a strong, random secret key in production

4. **Environment Variables**: Never commit `.env` files. Use your hosting platform's environment variable settings.

## SEO Configuration

The application includes:
- React Helmet for dynamic meta tags
- `robots.txt` in the public folder
- `sitemap.xml` in the public folder
- Semantic HTML structure
- Mobile-responsive design

**Remember to update:**
- `sitemap.xml` with your actual domain
- `robots.txt` with your actual domain
- Meta tags in each page component

## Development Tips

1. **Backend**: The Flask server runs in debug mode by default. Change this in production.

2. **Frontend**: Vite provides hot module replacement for fast development.

3. **MongoDB**: The app automatically creates an admin user on first run if none exists.

4. **Cart**: Cart data is stored in localStorage, so it persists across sessions.

## License

This project is open source and available for use.

## Support

For issues or questions, please check the code comments or create an issue in the repository.


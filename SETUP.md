# Setup Instructions

This guide will help you set up the Local Pharmacy application on your local machine.

## Prerequisites

- **Node.js** (v16 or higher) - [Download](https://nodejs.org/)
- **Python** (3.8 or higher) - [Download](https://www.python.org/downloads/)
- **MongoDB Atlas Account** (Free tier) - [Sign up](https://www.mongodb.com/cloud/atlas)
- **Git** (optional, for version control)

## Step 1: MongoDB Atlas Setup

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and create a free account
2. Create a new cluster (choose the free M0 tier)
3. Create a database user:
   - Go to **Database Access** → **Add New Database User**
   - Choose **Password** authentication
   - Create a username and password (save these!)
   - Set user privileges to **Read and write to any database**
4. Whitelist IP addresses:
   - Go to **Network Access** → **Add IP Address**
   - Click **Add Current IP Address** (for development)
   - Or add `0.0.0.0/0` to allow all IPs (less secure, but easier for development)
5. Get your connection string:
   - Go to **Database** → **Connect** → **Connect your application**
   - Copy the connection string
   - It will look like: `mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`
   - Replace `<username>` and `<password>` with your database user credentials
   - Add `/pharmacy` before the `?` to specify the database name: `mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/pharmacy?retryWrites=true&w=majority`

## Step 2: Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file:**
   Create a file named `.env` in the `backend` directory with the following content:
   ```env
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/pharmacy?retryWrites=true&w=majority
   JWT_SECRET_KEY=your-secret-key-change-in-production
   FLASK_ENV=development
   FLASK_DEBUG=True
   PORT=5000
   HOST=0.0.0.0
   ```
   
   **Important:**
   - Replace `MONGO_URI` with your actual MongoDB Atlas connection string
   - Replace `JWT_SECRET_KEY` with a strong random string (you can generate one using: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)

5. **Run the Flask server:**
   ```bash
   python app.py
   ```

   The backend will run on `http://localhost:5000`

   **Default Admin Credentials:**
   - Username: `admin`
   - Password: `admin123`
   
   ⚠️ **Important:** Change the admin password after first login in production!

## Step 3: Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create `.env` file:**
   Create a file named `.env` in the `frontend` directory with the following content:
   ```env
   VITE_API_URL=http://localhost:5000/api
   ```

4. **Run the development server:**
   ```bash
   npm run dev
   ```

   The frontend will run on `http://localhost:3000` (or the next available port)

5. **Build for production (optional):**
   ```bash
   npm run build
   ```
   
   This creates an optimized production build in the `dist` directory.

## Step 4: Verify Installation

1. **Backend:**
   - Open `http://localhost:5000/api/products` in your browser
   - You should see an empty array `[]` (no products yet)

2. **Frontend:**
   - Open `http://localhost:3000` in your browser
   - You should see the home page

3. **Admin Login:**
   - Navigate to `http://localhost:3000/admin/login`
   - Login with: `admin` / `admin123`
   - You should be redirected to the admin dashboard

4. **Add a test product:**
   - After logging in, go to **Admin → Products**
   - Click **+ Add Product**
   - Fill in the form and save
   - Go to **Products** page to see your product

## Troubleshooting

### Backend Issues

**MongoDB Connection Error:**
- Verify your connection string is correct
- Check that your IP is whitelisted in MongoDB Atlas
- Ensure your database user has proper permissions
- Check that you've added `/pharmacy` to the connection string

**Port Already in Use:**
- Change the `PORT` in `.env` to a different port (e.g., 5001)
- Or stop the process using port 5000

**Module Not Found:**
- Make sure you've activated your virtual environment
- Run `pip install -r requirements.txt` again

### Frontend Issues

**API Connection Error:**
- Verify `VITE_API_URL` in `.env` is correct
- Make sure the backend is running
- Check browser console for CORS errors

**Build Errors:**
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again
- Check Node.js version: `node --version` (should be 16+)

**Port Already in Use:**
- Vite will automatically use the next available port
- Or change the port in `vite.config.js`

## Project Structure

```
Pharmecy/
├── backend/
│   ├── app.py                 # Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── Procfile              # For deployment (Render/Railway)
│   └── .env                  # Environment variables (create this)
├── frontend/
│   ├── public/
│   │   ├── robots.txt        # SEO robots file
│   │   └── sitemap.xml       # SEO sitemap
│   ├── src/
│   │   ├── components/       # Reusable components
│   │   │   ├── Navbar.jsx
│   │   │   └── Footer.jsx
│   │   ├── context/          # React contexts
│   │   │   ├── AuthContext.jsx
│   │   │   └── CartContext.jsx
│   │   ├── pages/            # Page components
│   │   │   ├── admin/        # Admin pages
│   │   │   │   ├── AdminDashboard.jsx
│   │   │   │   ├── AdminLogin.jsx
│   │   │   │   ├── AdminProducts.jsx
│   │   │   │   ├── AdminOrders.jsx
│   │   │   │   └── AdminOffers.jsx
│   │   │   ├── Home.jsx
│   │   │   ├── Products.jsx
│   │   │   ├── Cart.jsx
│   │   │   ├── Checkout.jsx
│   │   │   └── OrderHistory.jsx
│   │   ├── services/
│   │   │   └── api.js        # API service
│   │   ├── App.jsx           # Main app component
│   │   ├── main.jsx          # Entry point
│   │   └── index.css         # Global styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── .env                  # Environment variables (create this)
├── README.md
├── SETUP.md                  # This file
└── DEPLOYMENT.md             # Deployment guide
```

## Next Steps

1. **Add Products:** Use the admin dashboard to add products
2. **Create Offers:** Add promotional codes in the admin dashboard
3. **Test Order Flow:** Add products to cart, checkout, and place an order
4. **View Orders:** Search for orders by phone number
5. **Customize:** Update pharmacy details, contact information, and styling

## Development Tips

1. **Hot Reload:** Both frontend (Vite) and backend (Flask debug mode) support hot reload
2. **Cart Persistence:** Cart is saved in localStorage, so it persists across sessions
3. **Admin Session:** Admin login uses JWT tokens stored in localStorage
4. **Database:** MongoDB Atlas provides a free tier with 512MB storage

## Security Notes

⚠️ **For Production:**
- Change default admin password
- Use a strong, random JWT_SECRET_KEY
- Restrict MongoDB Atlas IP whitelist to your server IPs only
- Set `FLASK_DEBUG=False` in production
- Use environment variables, never commit `.env` files
- Enable HTTPS (automatic on Netlify/Render/Railway)

## Support

If you encounter issues:
1. Check the error messages in the console/terminal
2. Verify all environment variables are set correctly
3. Ensure MongoDB Atlas is accessible
4. Check that all dependencies are installed
5. Review the DEPLOYMENT.md for production-specific issues


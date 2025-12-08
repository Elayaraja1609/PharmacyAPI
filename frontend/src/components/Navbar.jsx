import { Link, useLocation } from 'react-router-dom'
import { useCart } from '../context/CartContext'
import { useAuth } from '../context/AuthContext'

const Navbar = () => {
  const location = useLocation()
  const { getCartCount } = useCart()
  const { user, logout } = useAuth()
  const cartCount = getCartCount()

  const isActive = (path) => location.pathname === path

  return (
    <>
      {/* Top Bar */}
      <div className="bg-gray-900 text-white text-sm py-2">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span>📞</span>
              <span>CALL: +91 9000090000</span>
            </div>
            <div className="flex items-center gap-4">
              <a href="#" className="hover:text-teal-400 transition">📘</a>
              <a href="#" className="hover:text-teal-400 transition">🐦</a>
              <a href="#" className="hover:text-teal-400 transition">📷</a>
            </div>
          </div>
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="bg-black text-white shadow-lg sticky top-0 z-50">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-20">
            <Link to="/" className="flex items-center gap-2 text-2xl font-bold">
              <div className="w-10 h-10 bg-teal-500 rounded-full flex items-center justify-center">
                <span className="text-white text-xl">💊</span>
              </div>
              <span>MEDION</span>
            </Link>
            
            <div className="hidden md:flex items-center space-x-6">
              {!user ? (
                <>
                  <Link
                    to="/"
                    className={`px-3 py-2 font-semibold uppercase ${isActive('/') ? 'text-teal-400 border-b-2 border-teal-400' : 'hover:text-teal-400 transition'}`}
                  >
                    Home
                  </Link>
                  <Link
                    to="/products"
                    className={`px-3 py-2 font-semibold uppercase ${isActive('/products') ? 'text-teal-400 border-b-2 border-teal-400' : 'hover:text-teal-400 transition'}`}
                  >
                    Medicine
                  </Link>
                  <Link
                    to="/products"
                    className={`px-3 py-2 font-semibold uppercase ${isActive('/products') ? 'text-teal-400 border-b-2 border-teal-400' : 'hover:text-teal-400 transition'}`}
                  >
                    Online Buy
                  </Link>
                  <Link
                    to="/orders"
                    className={`px-3 py-2 font-semibold uppercase ${isActive('/orders') ? 'text-teal-400 border-b-2 border-teal-400' : 'hover:text-teal-400 transition'}`}
                  >
                    Orders
                  </Link>
                  <Link
                    to="/cart"
                    className="relative px-3 py-2 font-semibold uppercase hover:text-teal-400 transition"
                  >
                    Cart
                    {cartCount > 0 && (
                      <span className="absolute -top-1 -right-1 bg-teal-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                        {cartCount}
                      </span>
                    )}
                  </Link>
                </>
              ) : (
                <>
                  <Link
                    to="/admin"
                    className={`px-3 py-2 font-semibold uppercase ${isActive('/admin') ? 'text-teal-400 border-b-2 border-teal-400' : 'hover:text-teal-400 transition'}`}
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/admin/products"
                    className={`px-3 py-2 font-semibold uppercase ${isActive('/admin/products') ? 'text-teal-400 border-b-2 border-teal-400' : 'hover:text-teal-400 transition'}`}
                  >
                    Products
                  </Link>
                  <Link
                    to="/admin/orders"
                    className={`px-3 py-2 font-semibold uppercase ${isActive('/admin/orders') ? 'text-teal-400 border-b-2 border-teal-400' : 'hover:text-teal-400 transition'}`}
                  >
                    Orders
                  </Link>
                  <Link
                    to="/admin/offers"
                    className={`px-3 py-2 font-semibold uppercase ${isActive('/admin/offers') ? 'text-teal-400 border-b-2 border-teal-400' : 'hover:text-teal-400 transition'}`}
                  >
                    Offers
                  </Link>
                  <button
                    onClick={logout}
                    className="px-3 py-2 font-semibold uppercase hover:text-teal-400 transition"
                  >
                    Logout
                  </button>
                </>
              )}
            </div>

            {/* Mobile Menu Button */}
            <div className="md:hidden">
              <button className="text-white">
                ☰
              </button>
            </div>
          </div>
        </div>
      </nav>
    </>
  )
}

export default Navbar


import { Link } from 'react-router-dom'
import { useState } from 'react'

const Footer = () => {
  const [email, setEmail] = useState('')

  const handleSubscribe = (e) => {
    e.preventDefault()
    alert('Thank you for subscribing!')
    setEmail('')
  }

  return (
    <footer className="bg-black text-white mt-auto">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Contact */}
          <div>
            <h4 className="text-lg font-bold mb-4 uppercase">Contact</h4>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <span>📞</span>
                <span>+91 9000090000</span>
              </div>
              <div className="flex items-center gap-3">
                <span>✉️</span>
                <span>demo@gmail.com</span>
              </div>
            </div>
          </div>
          
          {/* Menu */}
          <div>
            <h4 className="text-lg font-bold mb-4 uppercase">Menu</h4>
            <ul className="space-y-2">
              <li>
                <Link to="/" className="text-gray-300 hover:text-teal-400 transition">
                  Home
                </Link>
              </li>
              <li>
                <Link to="/products" className="text-gray-300 hover:text-teal-400 transition">
                  Medicine
                </Link>
              </li>
              <li>
                <Link to="/products" className="text-gray-300 hover:text-teal-400 transition">
                  Online Buy
                </Link>
              </li>
              <li>
                <Link to="/orders" className="text-gray-300 hover:text-teal-400 transition">
                  Orders
                </Link>
              </li>
            </ul>
          </div>
          
          {/* Newsletter */}
          <div>
            <h4 className="text-lg font-bold mb-4 uppercase">Newsletter</h4>
            <form onSubmit={handleSubscribe} className="space-y-3">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter Your email"
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-teal-500"
                required
              />
              <button
                type="submit"
                className="bg-teal-500 text-white px-6 py-2 rounded font-semibold hover:bg-teal-600 transition w-full"
              >
                Subscribe
              </button>
            </form>
          </div>
        </div>
        
        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
          <p>&copy; {new Date().getFullYear()} All Rights Reserved</p>
        </div>
      </div>
    </footer>
  )
}

export default Footer


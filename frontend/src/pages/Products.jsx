import { useState, useEffect } from 'react'
import { Helmet } from 'react-helmet-async'
import api from '../services/api'
import { useCart } from '../context/CartContext'

const Products = () => {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const { addToCart } = useCart()

  useEffect(() => {
    fetchProducts()
  }, [])

  const fetchProducts = async () => {
    try {
      setLoading(true)
      const response = await api.get('/products')
      setProducts(response.data)
    } catch (error) {
      console.error('Error fetching products:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async () => {
    try {
      setLoading(true)
      const response = await api.get(`/products?search=${encodeURIComponent(searchTerm)}`)
      setProducts(response.data)
    } catch (error) {
      console.error('Error searching products:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddToCart = (product) => {
    if (product.stock > 0) {
      addToCart(product)
      alert(`${product.name} added to cart!`)
    } else {
      alert('Product is out of stock')
    }
  }

  return (
    <>
      <Helmet>
        <title>Products - Local Pharmacy</title>
        <meta name="description" content="Browse our wide selection of pharmaceutical products and health supplies." />
      </Helmet>

      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            VITAMINS & SUPPLEMENTS
            <div className="w-32 h-1 bg-teal-500 mx-auto mt-4"></div>
          </h1>
        </div>

        {/* Search Bar */}
        <div className="mb-8 max-w-2xl mx-auto">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <input
                type="text"
                placeholder="Search products..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="w-full px-4 py-3 pl-10 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
              <span className="absolute left-3 top-3.5 text-gray-400">🔍</span>
            </div>
            <button
              onClick={handleSearch}
              className="bg-teal-500 text-white px-8 py-3 rounded-lg hover:bg-teal-600 transition font-semibold"
            >
              Search
            </button>
            {searchTerm && (
              <button
                onClick={() => {
                  setSearchTerm('')
                  fetchProducts()
                }}
                className="bg-gray-500 text-white px-6 py-3 rounded-lg hover:bg-gray-600 transition"
              >
                Clear
              </button>
            )}
          </div>
        </div>

        {/* Products Grid */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading products...</p>
          </div>
        ) : products.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600 text-xl">No products found</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {products.map((product) => (
              <div key={product._id} className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition transform hover:-translate-y-1">
                <div className="relative">
                  {product.image ? (
                    <img
                      src={product.image}
                      alt={product.name}
                      className="w-full h-64 object-cover"
                    />
                  ) : (
                    <div className="w-full h-64 bg-gradient-to-br from-teal-100 to-teal-200 flex items-center justify-center relative">
                      <div className="flex gap-2">
                        <div className="w-12 h-12 bg-blue-500 rounded-full"></div>
                        <div className="w-12 h-12 bg-orange-500 rounded-full -ml-4"></div>
                      </div>
                    </div>
                  )}
                  <button
                    onClick={() => handleAddToCart(product)}
                    disabled={product.stock === 0}
                    className={`absolute top-2 right-2 px-4 py-2 rounded font-semibold text-sm transition ${
                      product.stock > 0
                        ? 'bg-black text-white hover:bg-gray-800'
                        : 'bg-gray-400 text-gray-600 cursor-not-allowed'
                    }`}
                  >
                    {product.stock > 0 ? 'Buy Now' : 'Out of Stock'}
                  </button>
                </div>
                <div className="p-4">
                  {/* Star Rating */}
                  <div className="flex items-center gap-1 mb-2">
                    {[...Array(5)].map((_, i) => (
                      <span key={i} className={i < 4 ? 'text-yellow-400' : 'text-gray-300'}>★</span>
                    ))}
                  </div>
                  <p className="text-xs text-gray-500 mb-2 uppercase">Health</p>
                  <h3 className="text-lg font-bold mb-2 line-clamp-1">{product.name}</h3>
                  {product.category && (
                    <p className="text-xs text-gray-500 mb-3">{product.category}</p>
                  )}
                  <div className="flex items-center justify-between">
                    <span className="text-2xl font-bold text-teal-600">
                      ${product.price.toFixed(2)}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded ${product.stock > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {product.stock > 0 ? `Stock: ${product.stock}` : 'Out of Stock'}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  )
}

export default Products


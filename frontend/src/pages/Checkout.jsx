import { useState, useEffect } from 'react'
import { Helmet } from 'react-helmet-async'
import { useNavigate } from 'react-router-dom'
import { useCart } from '../context/CartContext'
import api from '../services/api'

const Checkout = () => {
  const navigate = useNavigate()
  const { cart, getCartTotal, clearCart } = useCart()
  const [customer, setCustomer] = useState({
    name: '',
    phone: '',
    address: ''
  })
  const [offerCode, setOfferCode] = useState('')
  const [discount, setDiscount] = useState(0)
  const [appliedOffer, setAppliedOffer] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (cart.length === 0) {
      navigate('/cart')
    }
  }, [cart, navigate])

  const handleInputChange = (e) => {
    setCustomer({
      ...customer,
      [e.target.name]: e.target.value
    })
  }

  const handleApplyOffer = async () => {
    if (!offerCode.trim()) {
      setError('Please enter an offer code')
      return
    }

    try {
      const response = await api.get(`/offers/${offerCode.toUpperCase()}`)
      const offer = response.data
      setAppliedOffer(offer)
      
      const subtotal = getCartTotal()
      if (offer.type === 'percentage') {
        setDiscount(subtotal * (offer.value / 100))
      } else {
        setDiscount(Math.min(offer.value, subtotal))
      }
      setError('')
    } catch (error) {
      setError('Invalid or inactive offer code')
      setAppliedOffer(null)
      setDiscount(0)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!customer.name || !customer.phone || !customer.address) {
      setError('Please fill in all customer details')
      return
    }

    setLoading(true)

    try {
      const orderData = {
        customer,
        items: cart,
        total: getCartTotal(),
        offer_code: offerCode || undefined
      }

      const response = await api.post('/orders', orderData)
      clearCart()
      navigate(`/orders?orderId=${response.data._id}`)
    } catch (error) {
      setError(error.response?.data?.message || 'Failed to place order. Please try again.')
      setLoading(false)
    }
  }

  const finalTotal = Math.max(0, getCartTotal() - discount)

  return (
    <>
      <Helmet>
        <title>Checkout - Local Pharmacy</title>
      </Helmet>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Checkout</h1>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-2xl font-bold mb-4">Customer Details</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={customer.name}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Phone Number *
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    value={customer.phone}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Delivery Address *
                  </label>
                  <textarea
                    name="address"
                    value={customer.address}
                    onChange={handleInputChange}
                    required
                    rows="4"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold mb-4">Apply Offer Code</h2>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={offerCode}
                  onChange={(e) => setOfferCode(e.target.value.toUpperCase())}
                  placeholder="Enter offer code"
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  type="button"
                  onClick={handleApplyOffer}
                  className="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700 transition"
                >
                  Apply
                </button>
              </div>
              {appliedOffer && (
                <div className="mt-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
                  Offer applied: {appliedOffer.description || appliedOffer.code} - 
                  {appliedOffer.type === 'percentage' 
                    ? ` ${appliedOffer.value}% off`
                    : ` $${appliedOffer.value} off`}
                </div>
              )}
            </div>
          </div>

          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-4">
              <h2 className="text-2xl font-bold mb-4">Order Summary</h2>
              <div className="space-y-2 mb-4">
                <div className="flex justify-between">
                  <span>Subtotal:</span>
                  <span>${getCartTotal().toFixed(2)}</span>
                </div>
                {discount > 0 && (
                  <div className="flex justify-between text-green-600">
                    <span>Discount:</span>
                    <span>-${discount.toFixed(2)}</span>
                  </div>
                )}
                <div className="border-t pt-2 flex justify-between font-bold text-lg">
                  <span>Total:</span>
                  <span>${finalTotal.toFixed(2)}</span>
                </div>
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {loading ? 'Placing Order...' : 'Place Order'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </>
  )
}

export default Checkout


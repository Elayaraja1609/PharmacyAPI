import { useState, useEffect } from 'react'
import { Helmet } from 'react-helmet-async'
import { useSearchParams } from 'react-router-dom'
import api from '../services/api'

const OrderHistory = () => {
  const [searchParams] = useSearchParams()
  const orderId = searchParams.get('orderId')
  const [phone, setPhone] = useState('')
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    if (orderId) {
      fetchOrderById(orderId)
    }
  }, [orderId])

  const fetchOrderById = async (id) => {
    try {
      setLoading(true)
      const response = await api.get(`/orders/${id}`)
      setOrders([response.data])
      setSuccess('Order found!')
    } catch (error) {
      setError('Order not found')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!phone.trim()) {
      setError('Please enter a phone number')
      return
    }

    try {
      setLoading(true)
      setError('')
      setSuccess('')
      const response = await api.get(`/orders?phone=${encodeURIComponent(phone)}`)
      setOrders(response.data)
      if (response.data.length === 0) {
        setError('No orders found for this phone number')
      } else {
        setSuccess(`Found ${response.data.length} order(s)`)
      }
    } catch (error) {
      setError('Failed to fetch orders. Please try again.')
      setOrders([])
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      confirmed: 'bg-blue-100 text-blue-800',
      processing: 'bg-purple-100 text-purple-800',
      shipped: 'bg-indigo-100 text-indigo-800',
      delivered: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  return (
    <>
      <Helmet>
        <title>Order History - Local Pharmacy</title>
        <meta name="description" content="View your order history by entering your phone number." />
      </Helmet>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Order History</h1>

        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <form onSubmit={handleSearch} className="flex gap-4">
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="Enter your phone number"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={loading}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition disabled:bg-gray-400"
            >
              {loading ? 'Searching...' : 'Search Orders'}
            </button>
          </form>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
            {success}
          </div>
        )}

        {orders.length > 0 && (
          <div className="space-y-6">
            {orders.map((order) => (
              <div key={order._id} className="bg-white rounded-lg shadow-md p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-bold">Order #{order._id.slice(-8).toUpperCase()}</h3>
                    <p className="text-gray-600">
                      {new Date(order.created_at).toLocaleString()}
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getStatusColor(order.status)}`}>
                    {order.status.toUpperCase()}
                  </span>
                </div>

                <div className="mb-4">
                  <h4 className="font-semibold mb-2">Customer Details:</h4>
                  <p className="text-gray-600">
                    {order.customer.name}<br />
                    {order.customer.phone}<br />
                    {order.customer.address}
                  </p>
                </div>

                <div className="mb-4">
                  <h4 className="font-semibold mb-2">Items:</h4>
                  <div className="space-y-2">
                    {order.items.map((item, index) => (
                      <div key={index} className="flex justify-between text-gray-600">
                        <span>{item.name} x {item.quantity}</span>
                        <span>${(item.price * item.quantity).toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {order.offer_code && (
                  <div className="mb-4">
                    <p className="text-sm text-gray-600">
                      Offer Code: <span className="font-semibold">{order.offer_code}</span>
                    </p>
                  </div>
                )}

                <div className="border-t pt-4 flex justify-between items-center">
                  <div>
                    {order.discount > 0 && (
                      <p className="text-sm text-gray-600">
                        Subtotal: ${order.subtotal.toFixed(2)}<br />
                        Discount: -${order.discount.toFixed(2)}
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-blue-600">
                      ${order.total.toFixed(2)}
                    </p>
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

export default OrderHistory


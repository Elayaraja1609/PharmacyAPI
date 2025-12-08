import { Helmet } from 'react-helmet-async'
import { Link } from 'react-router-dom'
import { useState, useEffect } from 'react'
import api from '../services/api'

// Callback Request Form Component
const CallbackRequestForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    medicine: '',
    message: ''
  })
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchProducts()
  }, [])

  const fetchProducts = async () => {
    try {
      const response = await api.get('/products')
      setProducts(response.data)
    } catch (error) {
      console.error('Error fetching products:', error)
    }
  }

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess(false)

    if (!formData.name || !formData.phone) {
      setError('Name and Phone Number are required')
      return
    }

    setLoading(true)

    try {
      await api.post('/callback-requests', formData)
      setSuccess(true)
      setFormData({
        name: '',
        phone: '',
        email: '',
        medicine: '',
        message: ''
      })
      // Hide success message after 5 seconds
      setTimeout(() => setSuccess(false), 5000)
    } catch (error) {
      setError(error.response?.data?.message || 'Failed to submit request. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="py-16 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
          <div>
            <h2 className="text-3xl font-bold mb-6">
              REQUEST A CALL BACK
              <div className="w-24 h-1 bg-teal-500 mt-2"></div>
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                  {error}
                </div>
              )}
              {success && (
                <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
                  Thank you! We will call you back soon.
                </div>
              )}
              <div>
                <label className="block text-sm font-medium mb-2">Name *</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Your Name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Phone Number *</label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Your Phone"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Email</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Your Email"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Select Medicine</label>
                <select
                  name="medicine"
                  value={formData.medicine}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <option value="">Select a medicine (optional)</option>
                  {products.map((product) => (
                    <option key={product._id} value={product.name}>
                      {product.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Message</label>
                <textarea
                  name="message"
                  value={formData.message}
                  onChange={handleInputChange}
                  rows="4"
                  className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-teal-500"
                  placeholder="Your Message"
                ></textarea>
              </div>
              <button
                type="submit"
                disabled={loading}
                className="bg-black text-white px-8 py-3 rounded font-semibold hover:bg-gray-800 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {loading ? 'Sending...' : 'Send'}
              </button>
            </form>
          </div>
          <div className="bg-teal-500 text-white p-12 rounded-lg flex flex-col justify-center">
            <h3 className="text-4xl font-bold mb-6">Get Now Medicines</h3>
            <p className="text-teal-100 leading-relaxed">
              There are many variations of passages of Lorem ipsum available, but the majority have suffered alteration in some form, by injected humour, or randomised words which don't look even slightly believable.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}

// Testimonials Slider Component
const TestimonialsSlider = () => {
  const [testimonials, setTestimonials] = useState([])
  const [currentTestimonial, setCurrentTestimonial] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTestimonials()
  }, [])

  useEffect(() => {
    if (testimonials.length > 0) {
      const interval = setInterval(() => {
        setCurrentTestimonial((prev) => (prev + 1) % testimonials.length)
      }, 5000) // Change testimonial every 5 seconds

      return () => clearInterval(interval)
    }
  }, [testimonials.length])

  const fetchTestimonials = async () => {
    try {
      const response = await api.get('/testimonials?approved=true')
      setTestimonials(response.data)
    } catch (error) {
      console.error('Error fetching testimonials:', error)
    } finally {
      setLoading(false)
    }
  }

  const goToTestimonial = (index) => {
    setCurrentTestimonial(index)
  }

  const nextTestimonial = () => {
    setCurrentTestimonial((prev) => (prev + 1) % testimonials.length)
  }

  const prevTestimonial = () => {
    setCurrentTestimonial((prev) => (prev - 1 + testimonials.length) % testimonials.length)
  }

  if (loading) {
    return (
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600"></div>
          </div>
        </div>
      </section>
    )
  }

  if (testimonials.length === 0) {
    return (
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4">
              WHAT IS SAYS OUR <span className="text-teal-500">CLIENTS</span>
            </h2>
          </div>
          <div className="max-w-3xl mx-auto text-center">
            <p className="text-gray-600">No testimonials available yet.</p>
          </div>
        </div>
      </section>
    )
  }

  return (
    <section className="py-16 bg-white">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">
            WHAT IS SAYS OUR <span className="text-teal-500">CLIENTS</span>
          </h2>
        </div>
        <div className="max-w-3xl mx-auto relative">
          {/* Testimonials Slider */}
          <div className="relative overflow-hidden" style={{ minHeight: '300px' }}>
            {testimonials.map((testimonial, index) => (
              <div
                key={testimonial._id}
                className={`transition-opacity duration-1000 ${
                  currentTestimonial === index ? 'opacity-100' : 'opacity-0 absolute inset-0'
                }`}
              >
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 mb-6">
                  <p className="text-gray-600 text-center leading-relaxed">
                    "{testimonial.review}"
                  </p>
                </div>
                <div className="text-center">
                  <div className="w-20 h-20 bg-teal-100 rounded-full mx-auto mb-4 flex items-center justify-center">
                    <span className="text-3xl text-teal-600 font-bold">
                      {testimonial.customer_name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <h4 className="font-bold text-lg mb-1 uppercase">
                    {testimonial.customer_name}
                  </h4>
                  <p className="text-gray-500 mb-2">Client</p>
                  {/* Star Rating */}
                  <div className="flex justify-center gap-1 mb-2">
                    {[...Array(5)].map((_, i) => (
                      <span
                        key={i}
                        className={i < (testimonial.rating || 5) ? 'text-yellow-400' : 'text-gray-300'}
                      >
                        ★
                      </span>
                    ))}
                  </div>
                  <div className="text-teal-500 text-2xl">"</div>
                </div>
              </div>
            ))}
          </div>

          {/* Navigation Arrows */}
          {testimonials.length > 1 && (
            <>
              <button
                onClick={prevTestimonial}
                className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-4 bg-teal-500 text-white p-2 rounded-full hover:bg-teal-600 transition z-10"
                aria-label="Previous testimonial"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <button
                onClick={nextTestimonial}
                className="absolute right-0 top-1/2 transform -translate-y-1/2 translate-x-4 bg-teal-500 text-white p-2 rounded-full hover:bg-teal-600 transition z-10"
                aria-label="Next testimonial"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </>
          )}

          {/* Pagination Dots */}
          {testimonials.length > 1 && (
            <div className="flex justify-center gap-2 mt-8">
              {testimonials.map((_, index) => (
                <button
                  key={index}
                  onClick={() => goToTestimonial(index)}
                  className={`transition-all ${
                    currentTestimonial === index
                      ? 'w-8 h-3 bg-teal-500 rounded-full'
                      : 'w-3 h-3 bg-gray-300 rounded-full hover:bg-teal-300'
                  }`}
                  aria-label={`Go to testimonial ${index + 1}`}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  )
}

const Home = () => {
  const [currentSlide, setCurrentSlide] = useState(0)

  // Sample pharmacy shop images - replace these with your actual images
  const shopImages = [
    '/upload/pharmacy1.jpg',
    '/upload/pharmacy2.jpg',
    '/upload/pharmacy3.jpg',
    '/upload/pharmacy4.jpg',
    '/upload/pharmacy5.jpg',
  ]

  // Auto-slide functionality
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % (shopImages.length + 1))
    }, 5000) // Change slide every 5 seconds

    return () => clearInterval(interval)
  }, [shopImages.length])

  const goToSlide = (index) => {
    setCurrentSlide(index)
  }

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % (shopImages.length + 1))
  }

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + shopImages.length + 1) % (shopImages.length + 1))
  }

  return (
    <>
      <Helmet>
        <title>Medion - Online Medicine Store</title>
        <meta name="description" content="Your trusted online pharmacy providing quality medicines and health products. Fast delivery and expert consultation." />
        <meta name="keywords" content="pharmacy, medicines, health products, online pharmacy, prescription drugs" />
        <meta property="og:title" content="Medion - Online Medicine Store" />
        <meta property="og:description" content="Your trusted online pharmacy providing quality medicines and health products." />
        <meta property="og:type" content="website" />
      </Helmet>

      {/* Hero Slider Section */}
      <section className="relative overflow-hidden" style={{ height: '600px' }}>
        {/* Slide 1 - Welcome Content */}
        <div
          className={`absolute inset-0 transition-opacity duration-1000 ${
            currentSlide === 0 ? 'opacity-100 z-10' : 'opacity-0 z-0'
          }`}
        >
          <div className="bg-gradient-to-br from-teal-500 to-teal-600 text-white h-full flex items-center">
            <div className="container mx-auto px-4 w-full">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
                {/* Left Side - Text */}
                <div className="z-10">
                  <p className="text-teal-100 text-lg mb-2">Welcome To Our</p>
                  <h1 className="text-4xl md:text-6xl font-bold mb-6">
                    Online Medicine
                  </h1>
                  <p className="text-teal-100 mb-8 leading-relaxed">
                    There are many variations of passages of Lorem Ipsum available, but the majority have suffered alteration in some form, by injected humour, or randomised words which don't look even slightly believable.
                  </p>
                  <Link
                    to="/products"
                    className="bg-black text-white px-8 py-4 rounded-lg font-semibold hover:bg-gray-800 transition inline-block"
                  >
                    Buy Now
                  </Link>
                </div>

                {/* Right Side - Visual Element */}
                <div className="relative z-10">
                  <div className="flex justify-center items-center">
                    <div className="relative">
                      {/* Capsule Stack */}
                      <div className="flex flex-col items-center gap-2">
                        <div className="w-32 h-16 bg-teal-400 rounded-full"></div>
                        <div className="w-32 h-16 bg-teal-300 rounded-full"></div>
                        <div className="w-32 h-16 bg-teal-400 rounded-full"></div>
                        <div className="w-32 h-16 bg-teal-300 rounded-full"></div>
                      </div>
                      {/* Floating Pills */}
                      <div className="absolute -top-4 -left-4 w-12 h-12 bg-white rounded-full"></div>
                      <div className="absolute -top-2 -right-4 w-12 h-12 bg-teal-200 rounded-full"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            {/* Background Pattern */}
            <div className="absolute inset-0 opacity-10">
              <div className="absolute top-20 right-20 w-64 h-64 bg-white rounded-full"></div>
              <div className="absolute bottom-20 left-20 w-48 h-48 bg-white rounded-full"></div>
            </div>
          </div>
        </div>

        {/* Slides 2-6 - Pharmacy Shop Photos */}
        {shopImages.map((imagePath, index) => (
          <div
            key={index + 1}
            className={`absolute inset-0 transition-opacity duration-1000 ${
              currentSlide === index + 1 ? 'opacity-100 z-10' : 'opacity-0 z-0'
            }`}
          >
            <div className="relative w-full h-full">
              <img
                src={imagePath}
                alt={`Pharmacy Shop ${index + 1}`}
                className="w-full h-full object-cover"
                onError={(e) => {
                  // Fallback if image doesn't exist
                  e.target.style.display = 'none'
                  e.target.nextSibling.style.display = 'flex'
                }}
              />
              {/* Placeholder if image not found */}
              <div
                className="hidden w-full h-full bg-gradient-to-br from-teal-400 to-teal-600 text-white items-center justify-center"
                style={{ display: 'none' }}
              >
                <div className="text-center">
                  <div className="text-6xl mb-4">🏥</div>
                  <h2 className="text-3xl font-bold mb-2">Pharmacy Shop {index + 1}</h2>
                  <p className="text-teal-100">Place your image at: {imagePath}</p>
                </div>
              </div>
              {/* Overlay for better text readability */}
              <div className="absolute inset-0 bg-black bg-opacity-30"></div>
              {/* Optional: Add text overlay */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center text-white z-10">
                  <h2 className="text-4xl md:text-5xl font-bold mb-4">Our Pharmacy Shop</h2>
                  <p className="text-xl">Visit us in person for expert consultation</p>
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Navigation Arrows */}
        <button
          onClick={prevSlide}
          className="absolute left-4 top-1/2 transform -translate-y-1/2 z-20 bg-black bg-opacity-50 text-white p-3 rounded-full hover:bg-opacity-70 transition"
          aria-label="Previous slide"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <button
          onClick={nextSlide}
          className="absolute right-4 top-1/2 transform -translate-y-1/2 z-20 bg-black bg-opacity-50 text-white p-3 rounded-full hover:bg-opacity-70 transition"
          aria-label="Next slide"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>

        {/* Slide Indicators */}
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-20 flex gap-2">
          {[...Array(shopImages.length + 1)].map((_, index) => (
            <button
              key={index}
              onClick={() => goToSlide(index)}
              className={`w-3 h-3 rounded-full transition ${
                currentSlide === index
                  ? 'bg-white w-8'
                  : 'bg-white bg-opacity-50 hover:bg-opacity-75'
              }`}
              aria-label={`Go to slide ${index + 1}`}
            />
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div className="text-5xl mb-4">🚚</div>
              <h3 className="text-xl font-bold mb-3 uppercase">Fast Delivery</h3>
              <p className="text-gray-600">
                It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout.
              </p>
            </div>
            <div className="text-center p-6">
              <div className="text-5xl mb-4">📜</div>
              <h3 className="text-xl font-bold mb-3 uppercase">License of Government</h3>
              <p className="text-gray-600">
                It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout.
              </p>
            </div>
            <div className="text-center p-6">
              <div className="text-5xl mb-4">🕐</div>
              <h3 className="text-xl font-bold mb-3 uppercase">Support 24/7</h3>
              <p className="text-gray-600">
                It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Discount Banner */}
      <section className="py-16 bg-black text-white">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl md:text-5xl font-bold mb-4">
                YOU GET ANY MEDICINE
              </h2>
              <h2 className="text-4xl md:text-5xl font-bold text-teal-400 mb-6">
                ON 10% DISCOUNT
              </h2>
              <p className="text-gray-300 mb-8">
                It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout.
              </p>
              <Link
                to="/products"
                className="bg-teal-500 text-white px-8 py-4 rounded-lg font-semibold hover:bg-teal-600 transition inline-block"
              >
                Buy Now
              </Link>
            </div>
            <div className="relative">
              {/* Pills Scattered */}
              <div className="flex flex-wrap gap-4 justify-center">
                {[...Array(12)].map((_, i) => (
                  <div
                    key={i}
                    className={`w-12 h-12 rounded-full ${
                      i % 2 === 0 ? 'bg-blue-500' : 'bg-white'
                    }`}
                    style={{
                      transform: `rotate(${Math.random() * 360}deg)`,
                      margin: `${Math.random() * 20}px`
                    }}
                  ></div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* About Us Section */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <button className="bg-gray-800 text-white px-6 py-2 rounded mb-4">
              See more
            </button>
            <h2 className="text-4xl font-bold mb-4">
              ABOUT US
              <div className="w-24 h-1 bg-teal-500 mx-auto mt-2"></div>
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <div className="flex justify-center">
              {/* Vitamin Bottles Illustration */}
              <div className="flex gap-4 items-end">
                <div className="text-center">
                  <div className="w-24 h-32 bg-white border-2 border-gray-300 rounded-lg mb-2 flex flex-col items-center justify-end pb-2">
                    <div className="w-16 h-20 bg-red-100 rounded"></div>
                  </div>
                  <div className="bg-green-500 text-white text-xs px-2 py-1 rounded">VITAMIN C</div>
                </div>
                <div className="text-center">
                  <div className="w-24 h-32 bg-white border-2 border-gray-300 rounded-lg mb-2 flex flex-col items-center justify-end pb-2">
                    <div className="w-16 h-20 bg-yellow-100 rounded"></div>
                  </div>
                  <div className="bg-green-500 text-white text-xs px-2 py-1 rounded">VITAMIN B12</div>
                </div>
              </div>
            </div>
            <div>
              <p className="text-gray-600 leading-relaxed">
                It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <TestimonialsSlider />

      {/* Request Call Back Section */}
      <CallbackRequestForm />
    </>
  )
}

export default Home

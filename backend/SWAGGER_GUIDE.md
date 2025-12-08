# Swagger API Documentation Guide

The Local Pharmacy API now includes Swagger/OpenAPI documentation for easy API exploration and testing.

## Installation

1. Install the required package:
```bash
pip install flasgger
```

Or if you're using requirements.txt:
```bash
pip install -r requirements.txt
```

## Accessing Swagger UI

After starting the Flask server, access Swagger UI at:

**http://localhost:5000/api-docs**

Or if running on a different host/port:
**http://127.0.0.1:5000/api-docs**

## Features

### 1. Interactive API Documentation
- Browse all available endpoints
- See request/response schemas
- View example requests and responses
- Test endpoints directly from the browser

### 2. Try It Out
- Click "Try it out" on any endpoint
- Fill in the required parameters
- Execute the request
- See the actual response

### 3. Authentication
- Admin endpoints require JWT authentication
- Use the "Authorize" button at the top
- Enter your JWT token (get it from `/api/admin/login`)
- Format: `Bearer <your-token>` or just `<your-token>`

## Documented Endpoints

Currently documented endpoints include:

#### Admin
- `POST /api/admin/login` - Admin login
- `GET /api/admin/stats` - Dashboard statistics (requires auth)

#### Products
- `GET /api/products` - Get all products (with search)

#### Orders
- `POST /api/orders` - Create new order

## Adding More Documentation

To add Swagger documentation to other endpoints, add a docstring in YAML format:

```python
@app.route('/api/your-endpoint', methods=['GET'])
def your_function():
    """
    Your Endpoint Description
    ---
    tags:
      - YourTag
    summary: Brief summary
    description: Detailed description
    parameters:
      - in: query
        name: param_name
        type: string
        required: false
    responses:
      200:
        description: Success response
        schema:
          type: object
          properties:
            key:
              type: string
    """
    # Your code here
    pass
```

## API Specification

The OpenAPI specification (JSON) is available at:
**http://localhost:5000/apispec.json**

This can be imported into tools like:
- Postman
- Insomnia
- API clients
- Code generators

## Testing with Swagger

### Example: Testing Admin Login

1. Go to `/api-docs`
2. Find "Admin" → "POST /api/admin/login"
3. Click "Try it out"
4. Enter request body:
```json
{
  "username": "admin",
  "password": "admin123"
}
```
5. Click "Execute"
6. Copy the `access_token` from the response

### Example: Testing with Authentication

1. First, login and get your token (see above)
2. Click "Authorize" button at the top
3. Enter: `Bearer <your-token>`
4. Now you can test protected endpoints like `/api/admin/stats`

## Troubleshooting

### Swagger UI not loading?
- Make sure `flasgger` is installed: `pip install flasgger`
- Check that Flask server is running
- Try accessing `/apispec.json` directly

### Authentication not working?
- Make sure you're using the correct format: `Bearer <token>` or just `<token>`
- Verify your token is still valid (tokens expire after 24 hours)
- Try logging in again to get a fresh token

### CORS errors?
- The backend has CORS enabled, but if you see errors, check the CORS configuration in `app.py`

## Additional Resources

- [Flasgger Documentation](https://github.com/flasgger/flasgger)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)


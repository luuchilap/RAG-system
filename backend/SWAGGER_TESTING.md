# Swagger UI Testing Guide

FastAPI automatically generates interactive API documentation using Swagger UI. This guide will help you test the API easily.

## Accessing Swagger UI

1. **Start the backend server:**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Open Swagger UI in your browser:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc (alternative): http://localhost:8000/redoc

## Testing Workflow

### 1. Register a New User

1. Navigate to the `/api/auth/register` endpoint
2. Click "Try it out"
3. Enter the request body:
   ```json
   {
     "username": "testuser",
     "email": "test@example.com",
     "password": "testpassword123"
   }
   ```
4. Click "Execute"
5. **Copy the `access_token` from the response** - you'll need it for authenticated endpoints

### 2. Login (Alternative to Register)

1. Navigate to the `/api/auth/login` endpoint
2. Click "Authorize" button at the top of the page
3. Enter:
   - Username: `testuser` (or your email)
   - Password: `testpassword123`
4. Click "Authorize"
5. The token will be automatically included in subsequent requests

### 3. Test Authenticated Endpoints

1. Click the "Authorize" button at the top of the Swagger UI
2. Enter your access token (from register/login response)
3. Click "Authorize"
4. Now you can test protected endpoints like `/api/auth/me`

## Available Endpoints

### Authentication (`/api/auth`)
- **POST `/register`** - Register a new user
- **POST `/login`** - Login and get access token
- **POST `/logout`** - Logout (client-side token removal)
- **GET `/me`** - Get current user info (requires authentication)

### Chat (`/api/chat`)
- Placeholder endpoints (to be implemented)

### Documents (`/api/documents`)
- Placeholder endpoints (to be implemented)

### RAG (`/api/rag`)
- Placeholder endpoints (to be implemented)

## Tips for Testing

1. **Use the "Authorize" button** - This automatically adds the Bearer token to all requests
2. **Check response examples** - Each endpoint shows example responses
3. **View request/response schemas** - Click "Schema" to see the data structure
4. **Try different status codes** - Test error cases (e.g., duplicate registration)

## Common Test Scenarios

### Test User Registration
```json
POST /api/auth/register
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123"
}
```

### Test Duplicate Registration (should fail)
```json
POST /api/auth/register
{
  "username": "johndoe",  // Same username
  "email": "different@example.com",
  "password": "securepass123"
}
```

### Test Login
```
POST /api/auth/login
Username: johndoe
Password: securepass123
```

### Test Get Current User (requires auth)
```
GET /api/auth/me
Authorization: Bearer <your-token>
```

## Troubleshooting

- **Database connection errors**: Make sure PostgreSQL is running and the database exists
- **401 Unauthorized**: Make sure you've authorized with a valid token
- **400 Bad Request**: Check that your request body matches the schema
- **500 Internal Server Error**: Check server logs for details


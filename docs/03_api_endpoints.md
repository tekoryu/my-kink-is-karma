# API Endpoints Documentation

## Base URL
```
http://localhost:8000/api/
```

## Authentication Endpoints

### POST /auth/login/
Login with username and password.

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "your-jwt-token-here",
  "user": {
    "id": 1,
    "username": "user@example.com",
    "email": "user@example.com"
  }
}
```

### POST /auth/register/
Register a new user.

**Request Body:**
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "password123",
  "password_confirm": "password123"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 2,
    "username": "newuser",
    "email": "newuser@example.com"
  }
}
```

### POST /auth/logout/
Logout and invalidate token.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

## User Endpoints

### GET /users/profile/
Get current user profile.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "username": "user@example.com",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "date_joined": "2024-01-01T00:00:00Z"
}
```

### PUT /users/profile/
Update current user profile.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "user@example.com",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "date_joined": "2024-01-01T00:00:00Z"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Validation error",
  "details": {
    "field_name": ["Error message"]
  }
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication credentials were not provided"
}
```

### 403 Forbidden
```json
{
  "error": "You do not have permission to perform this action"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

## Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

# Recipe Recommender API Documentation

This document provides comprehensive documentation for the Recipe Recommender API endpoints.

## Base URL

- **Development**: `http://localhost:8080/api`
- **Production**: `https://yourdomain.com/api`

## Authentication

The API uses Flask-Login session-based authentication. Authenticated endpoints require a valid user session.

### Session Management

- Sessions are managed via HTTP cookies
- Login required endpoints return 401 if not authenticated
- CSRF protection is enabled for state-changing operations

## Response Format

All API responses return JSON with the following general structure:

**Success Response:**
```json
{
  "success": true,
  "data": {...},
  "message": "Success message"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error description",
  "message": "User-friendly error message"
}
```

## Rate Limiting

The API implements rate limiting for password reset requests:

- **Per IP**: 5 requests per hour (configurable via `RATE_LIMIT_PER_IP_PER_HOUR`)
- **Per Email**: 3 requests per hour (configurable via `RATE_LIMIT_PER_EMAIL_PER_HOUR`)

## Endpoints

### Authentication Endpoints

#### Register User

```http
POST /api/register
```

**Description:** Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "country": "United States",           // optional
  "newsletter_signup": false            // optional, default: false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Account created successfully"
}
```

**Error Responses:**
- `400`: Missing required fields or email already registered
- `500`: Registration failed due to server error

---

#### Login User

```http
POST /api/login
```

**Description:** Authenticate user and create session.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "user": "user@example.com"
}
```

**Error Responses:**
- `400`: No data provided
- `401`: Invalid credentials

---

#### Get Current User

```http
GET /api/auth/me
```

**Description:** Get information about the currently authenticated user.

**Response (Authenticated):**
```json
{
  "authenticated": true,
  "user": {
    "id": 123,
    "email": "user@example.com"
  }
}
```

**Response (Not Authenticated):**
```json
{
  "authenticated": false
}
```

**Status Codes:**
- `200`: User information returned
- `401`: Not authenticated

---

#### Logout User

```http
POST /api/logout
```

**Description:** End user session.

**Authentication:** Required

**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

#### Request Password Reset

```http
POST /api/forgot-password
```

**Description:** Request a password reset email. Response is consistent regardless of whether email exists for security.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "If that email exists, a reset link has been sent."
}
```

**Development Mode Response:**
```json
{
  "success": true,
  "message": "Password reset link generated (development mode).",
  "devResetToken": "abc123..."
}
```

**Rate Limiting:** Enforced per IP and email address.

---

#### Reset Password

```http
POST /api/reset-password
```

**Description:** Reset user password using a valid reset token.

**Request Body:**
```json
{
  "token": "reset-token-from-email",
  "password": "newpassword123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password has been reset"
}
```

**Error Responses:**
- `400`: Invalid request or missing data
- `400`: Invalid or expired token
- `500`: Password reset failed

---

### Recipe Endpoints

#### Search Recipes

```http
GET /api/search
```

**Description:** Search and filter recipes based on various criteria.

**Query Parameters:**
- `query` (string): Text search query
- `complexity_score` (float): Desired complexity (0-100)
- `number_of_ingredients` (int): Desired number of ingredients (≥1)
- `cook_time` (int): Desired cook time in minutes (≥1)
- `cuisine` (string): Cuisine filter (case-insensitive)
- `dietary_restrictions` (string): Comma-separated dietary tags
- `page` (int): Page number (default: 1)
- `limit` (int): Results per page (1-100, default: 20)

**Example Request:**
```http
GET /api/search?query=chicken&cuisine=italian&page=1&limit=10
```

**Response:**
```json
{
  "recipes": [
    {
      "id": "12345",
      "name": "Chicken Parmesan",
      "description": "Classic Italian-American dish",
      "cookTime": 45,
      "difficulty": "medium",
      "ingredients": ["chicken breast", "parmesan cheese", "..."],
      "instructions": ["Step 1", "Step 2", "..."],
      "cuisine": "Italian",
      "dietaryTags": ["gluten-free"],
      "complexityScore": 65.5,
      "imageUrl": "https://example.com/image.jpg"
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 10,
  "hasMore": true
}
```

**Error Responses:**
- `400`: Invalid parameter values
- `500`: Search failed or recommender unavailable

---

#### Get Recipe Details

```http
GET /api/recipes/{recipe_id}
```

**Description:** Get detailed information for a specific recipe.

**Path Parameters:**
- `recipe_id` (string): Recipe identifier

**Response:**
```json
{
  "recipe": {
    "id": "12345",
    "name": "Chicken Parmesan",
    "description": "Classic Italian-American dish",
    "cookTime": 45,
    "difficulty": "medium",
    "ingredients": ["chicken breast", "parmesan cheese", "..."],
    "instructions": ["Step 1", "Step 2", "..."],
    "cuisine": "Italian",
    "dietaryTags": ["gluten-free"],
    "complexityScore": 65.5,
    "imageUrl": "https://example.com/image.jpg"
  }
}
```

**Error Responses:**
- `404`: Recipe not found
- `500`: Failed to retrieve recipe or recommender unavailable

---

#### Get Enriched Ingredients

```http
GET /api/recipes/{recipe_id}/enriched-ingredients
```

**Description:** Get parsed ingredient information with quantities, units, and preparation methods.

**Path Parameters:**
- `recipe_id` (string): Recipe identifier

**Response:**
```json
{
  "recipeId": "12345",
  "originalIngredients": ["2 cups flour", "1 tsp salt"],
  "detailedIngredients": ["2 cups flour", "1 tsp salt"],
  "parsedIngredients": [
    {
      "original": "2 cups flour",
      "quantity": 2,
      "unit": "cups",
      "name": "flour",
      "preparation": null
    },
    {
      "original": "1 tsp salt",
      "quantity": 1,
      "unit": "tsp",
      "name": "salt",
      "preparation": null
    }
  ]
}
```

**Error Responses:**
- `404`: Recipe not found
- `500`: Failed to parse ingredients or recommender unavailable

---

### Saved Recipes Endpoints

#### Get Saved Recipes

```http
GET /api/saved-recipes
```

**Description:** Get list of user's saved recipes.

**Authentication:** Required

**Response:**
```json
{
  "recipes": [
    {"id": "12345"},
    {"id": "67890"}
  ]
}
```

**Error Responses:**
- `401`: Authentication required
- `500`: Failed to retrieve saved recipes

---

#### Save Recipe

```http
POST /api/saved-recipes
```

**Description:** Save a recipe to user's collection.

**Authentication:** Required

**Request Body:**
```json
{
  "recipe_id": "12345"
}
```

**Response:**
```json
{
  "message": "Recipe saved successfully"
}
```

**Error Responses:**
- `400`: Missing recipe_id or recipe not found
- `400`: Recipe already saved
- `401`: Authentication required
- `500`: Failed to save recipe

---

#### Remove Saved Recipe

```http
DELETE /api/saved-recipes/{recipe_id}
```

**Description:** Remove a recipe from user's saved collection.

**Authentication:** Required

**Path Parameters:**
- `recipe_id` (string): Recipe identifier

**Response:**
```json
{
  "message": "Recipe removed from saved recipes"
}
```

**Error Responses:**
- `401`: Authentication required
- `404`: Recipe not found in saved recipes
- `500`: Failed to remove saved recipe

---

### Admin Endpoints

All admin endpoints require the `X-Admin-Token` header with a valid admin token.

#### Check Email Configuration

```http
GET /api/admin/status/email
```

**Description:** Check email service configuration and status.

**Headers:**
```
X-Admin-Token: your-admin-token
```

**Response:**
```json
{
  "resend_available": true,
  "has_api_key": true,
  "email_from": "noreply@example.com",
  "frontend_base_url": "https://yourdomain.com",
  "environment": "production"
}
```

**Error Responses:**
- `403`: Forbidden (invalid admin token)

---

#### Send Test Email

```http
POST /api/admin/test-email
```

**Description:** Send a test email to verify email configuration.

**Headers:**
```
X-Admin-Token: your-admin-token
```

**Request Body:**
```json
{
  "to": "test@example.com"
}
```

**Response:**
```json
{
  "success": true
}
```

**Error Responses:**
- `400`: Missing 'to' field
- `403`: Forbidden (invalid admin token)
- `500`: Email sending failed

---

#### Check Rate Limits

```http
GET /api/admin/rate-limit?email=user@example.com&ip=192.168.1.1
```

**Description:** Check rate limiting status for specific email/IP.

**Headers:**
```
X-Admin-Token: your-admin-token
```

**Query Parameters:**
- `email` (string, optional): Email address to check
- `ip` (string, optional): IP address to check

**Response:**
```json
{
  "query": {
    "email": "user@example.com",
    "ip": "192.168.1.1"
  },
  "counts": {
    "email_1h": 2,
    "email_24h": 5,
    "ip_1h": 3,
    "ip_24h": 8
  }
}
```

**Error Responses:**
- `403`: Forbidden (invalid admin token)

---

#### Clear Reset Data

```http
POST /api/admin/maintenance/clear-reset-data
```

**Description:** Clean up old password reset tokens and request logs.

**Headers:**
```
X-Admin-Token: your-admin-token
```

**Request Body:**
```json
{
  "days": 7
}
```

**Response:**
```json
{
  "success": true,
  "deleted": {
    "logs": 25,
    "tokens": 10
  },
  "cutoff": "2024-01-01T00:00:00Z"
}
```

**Error Responses:**
- `403`: Forbidden (invalid admin token)
- `500`: Cleanup failed

---

### Miscellaneous Endpoints

#### Health Check

```http
GET /api/health
```

**Description:** Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

---

## Error Handling

### Common Error Codes

- **400 Bad Request**: Invalid input parameters or malformed request
- **401 Unauthorized**: Authentication required or invalid credentials
- **403 Forbidden**: Access denied (typically admin endpoints)
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error or service unavailable

### Error Response Format

```json
{
  "success": false,
  "error": "Detailed error description",
  "message": "User-friendly error message"
}
```

## Data Models

### Recipe Object

```typescript
interface Recipe {
  id: string;
  name: string;
  description: string;
  cookTime: number;              // minutes
  difficulty: string;            // "easy", "medium", "hard"
  ingredients: string[];
  instructions: string[];
  cuisine: string;
  dietaryTags: string[];
  complexityScore: number;       // 0-100
  imageUrl: string;
}
```

### User Object

```typescript
interface User {
  id: number;
  email: string;
  full_name: string;
  country?: string;
  newsletter_signup: boolean;
  created_at: string;            // ISO timestamp
}
```

### Parsed Ingredient Object

```typescript
interface ParsedIngredient {
  original: string;              // Original ingredient string
  quantity: number;              // Numeric quantity
  unit: string;                  // Unit of measurement
  name: string;                  // Ingredient name
  preparation: string | null;    // Preparation method
}
```

## Rate Limiting Details

### Password Reset Rate Limits

The system implements two types of rate limiting for password reset requests:

1. **IP-based limiting**: Prevents abuse from a single IP address
2. **Email-based limiting**: Prevents targeting specific email addresses

### Configuration

Rate limits are configurable via environment variables:

```env
RATE_LIMIT_PER_IP_PER_HOUR=5        # Default: 5
RATE_LIMIT_PER_EMAIL_PER_HOUR=3     # Default: 3
```

### Behavior

- Rate limits are enforced per rolling hour window
- Exceeded limits return the same success response for security
- Admin endpoints can check current rate limit status

## Security Considerations

### CSRF Protection

- All POST/PUT/DELETE endpoints are protected against CSRF attacks
- Frontend must include CSRF tokens with state-changing requests

### Password Security

- Passwords are hashed using Werkzeug's secure password hashing
- No password complexity requirements enforced by default
- Reset tokens are cryptographically secure and time-limited

### Email Security

- Password reset emails use secure, time-limited tokens
- Email addresses are normalized to lowercase for consistency
- Generic responses prevent email enumeration attacks

### Session Security

- Sessions use secure, HttpOnly cookies
- Session data is signed with the Flask SECRET_KEY
- Login required endpoints properly validate authentication

## Environment Configuration

### Required Environment Variables

```env
SECRET_KEY=your-secret-key           # Flask session secret
DATABASE_URL=postgresql://...        # Database connection (optional)
RESEND_API_KEY=re_...               # Resend API key for emails
EMAIL_FROM=noreply@yourdomain.com   # Verified sender address
FRONTEND_BASE_URL=https://...       # Base URL for reset links
ADMIN_TOKEN=your-admin-token        # Admin API access token
```

### Optional Environment Variables

```env
ENV=production                      # Environment mode
RATE_LIMIT_PER_IP_PER_HOUR=5       # IP rate limit
RATE_LIMIT_PER_EMAIL_PER_HOUR=3    # Email rate limit
MODEL_PATH=/path/to/model.joblib    # ML model file path
SQLITE_DIR=/data                    # SQLite directory (if not using PostgreSQL)
```

## Integration Examples

### Frontend Authentication Flow

```javascript
// Register user
const response = await fetch('/api/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123',
    full_name: 'John Doe'
  })
});

// Login user
const loginResponse = await fetch('/api/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});

// Check authentication status
const authResponse = await fetch('/api/auth/me');
const { authenticated, user } = await authResponse.json();
```

### Recipe Search Example

```javascript
// Search recipes with filters
const searchParams = new URLSearchParams({
  query: 'chicken',
  cuisine: 'italian',
  cook_time: '30',
  page: '1',
  limit: '20'
});

const response = await fetch(`/api/search?${searchParams}`);
const { recipes, total, hasMore } = await response.json();
```

### Admin Operations Example

```javascript
// Check email configuration
const response = await fetch('/api/admin/status/email', {
  headers: { 'X-Admin-Token': 'your-admin-token' }
});

// Send test email
const testResponse = await fetch('/api/admin/test-email', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Admin-Token': 'your-admin-token'
  },
  body: JSON.stringify({ to: 'test@example.com' })
});
```
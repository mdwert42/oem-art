from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from .database import create_tables
from .routers import auth_router

# Extended API description with authentication guide
API_DESCRIPTION = """
## Art.OEM API

Portfolio and e-commerce API for 3D printed and painted artwork.

---

## Authentication Guide

This API uses **JWT (JSON Web Token)** Bearer authentication for secure access to protected endpoints.

### Quick Start

#### 1. Login and Get Token

**Request:**
```bash
curl -X POST "http://localhost:8000/auth/login" \\
     -H "Content-Type: application/x-www-form-urlencoded" \\
     -d "username=admin&password=changeme"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 2. Use Token in Requests

Include the token in the `Authorization` header:

```bash
curl -X GET "http://localhost:8000/auth/me" \\
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Authentication Flow

```
┌─────────┐                 ┌─────────┐
│ Client  │                 │  Server │
└────┬────┘                 └────┬────┘
     │                           │
     │  POST /auth/login         │
     │  (username + password)    │
     │──────────────────────────>│
     │                           │
     │  JWT Token                │
     │<──────────────────────────│
     │                           │
     │  GET /auth/me             │
     │  (Authorization: Bearer)  │
     │──────────────────────────>│
     │                           │
     │  User Info                │
     │<──────────────────────────│
     │                           │
```

### Token Details

- **Expiration:** Tokens expire after **30 minutes** (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Algorithm:** HS256 (HMAC with SHA-256)
- **Token Claims:**
  - `sub`: Username
  - `user_id`: User's database ID
  - `role`: User role (admin or public)
  - `exp`: Expiration timestamp

### Code Examples

#### Python (requests library)

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/auth/login",
    data={"username": "admin", "password": "changeme"}
)
token = response.json()["access_token"]

# Use token for authenticated requests
headers = {"Authorization": f"Bearer {token}"}
user_info = requests.get(
    "http://localhost:8000/auth/me",
    headers=headers
).json()

print(f"Logged in as: {user_info['username']}")
```

#### JavaScript (fetch API)

```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
        username: 'admin',
        password: 'changeme'
    })
});

const { access_token } = await loginResponse.json();

// Store token
localStorage.setItem('access_token', access_token);

// Use token for authenticated requests
const userResponse = await fetch('http://localhost:8000/auth/me', {
    headers: {
        'Authorization': `Bearer ${access_token}`
    }
});

const userInfo = await userResponse.json();
console.log(`Logged in as: ${userInfo.username}`);
```

#### cURL

```bash
# Login and extract token
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \\
     -H "Content-Type: application/x-www-form-urlencoded" \\
     -d "username=admin&password=changeme" | jq -r '.access_token')

# Use token
curl -X GET "http://localhost:8000/auth/me" \\
     -H "Authorization: Bearer $TOKEN"
```

### User Roles

The system uses a simple two-tier role system:

| Role | Description | Access Level |
|------|-------------|--------------|
| **admin** | Site owner/administrator | Full access to all features |
| **public** | Regular user | Limited access |

### Common Error Scenarios

#### 401 Unauthorized - Invalid Credentials
```json
{
  "detail": "Incorrect username or password"
}
```
**Solution:** Check username and password are correct.

#### 401 Unauthorized - Invalid Token
```json
{
  "detail": "Could not validate credentials"
}
```
**Solutions:**
- Token may be expired (tokens last 30 minutes)
- Token may be malformed
- Get a new token by logging in again

#### 400 Bad Request - Inactive User
```json
{
  "detail": "Inactive user"
}
```
**Solution:** User account has been deactivated. Contact administrator.

#### 401 Unauthorized - Missing Token
```json
{
  "detail": "Not authenticated"
}
```
**Solution:** Include the Authorization header with Bearer token.

### Security Best Practices

1. **Store tokens securely:**
   - Use httpOnly cookies for web applications
   - Avoid localStorage for sensitive applications
   - Clear tokens on logout

2. **Handle token expiration:**
   - Implement token refresh logic
   - Redirect to login on 401 errors
   - Store expiration time with token

3. **HTTPS in Production:**
   - Always use HTTPS in production
   - Never send tokens over unencrypted connections

4. **Token Rotation:**
   - Consider implementing refresh tokens
   - Rotate tokens periodically
   - Implement token blacklisting for immediate revocation

### Testing with Swagger UI

1. Navigate to `/docs` (Swagger UI)
2. Click the **Authorize** button (lock icon)
3. Enter credentials in the OAuth2 form:
   - Username: `admin`
   - Password: `changeme`
4. Click **Authorize**
5. Try protected endpoints - they should now work!

Alternatively, if you already have a token:
1. Click **Authorize**
2. Enter: `Bearer <your_token>`
3. Click **Authorize**

---

## Support

For issues or questions, please contact the API administrator.
"""

# Create FastAPI application
app = FastAPI(
    title="Art.OEM API",
    description=API_DESCRIPTION,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Art.OEM",
        "email": "admin@art.oem",
    },
    license_info={
        "name": "Private",
    }
)

# CORS middleware configuration
# TODO: Update allowed origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Event handler for startup
@app.on_event("startup")
async def startup_event():
    """
    Actions to perform on application startup.
    Creates database tables if they don't exist.
    """
    print("Starting up Art.OEM API...")
    create_tables()
    print("Database tables created/verified")


# Include routers
app.include_router(auth_router)


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint - API health check.
    """
    return {
        "message": "Art.OEM API",
        "version": "0.1.0",
        "status": "running"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {"status": "healthy"}

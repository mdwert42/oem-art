from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Dict, Any

from ..database import get_db
from ..models.user import User
from ..schemas.auth import Token, LoginRequest
from ..schemas.user import UserResponse
from ..auth.utils import verify_password, create_access_token
from ..auth.dependencies import get_current_active_user
from ..auth.config import AuthConfig

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={
        401: {
            "description": "Authentication failed",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_credentials": {
                            "summary": "Invalid credentials",
                            "value": {"detail": "Incorrect username or password"}
                        },
                        "missing_token": {
                            "summary": "Missing authentication token",
                            "value": {"detail": "Not authenticated"}
                        },
                        "invalid_token": {
                            "summary": "Invalid or expired token",
                            "value": {"detail": "Could not validate credentials"}
                        }
                    }
                }
            }
        }
    }
)


@router.post(
    "/login",
    response_model=Token,
    responses={
        200: {
            "description": "Successfully authenticated",
            "content": {
                "application/json": {
                    "examples": {
                        "successful_login": {
                            "summary": "Successful login",
                            "value": {
                                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjEsInJvbGUiOiJhZG1pbiIsImV4cCI6MTY0MDAwMDAwMH0.signature",
                                "token_type": "bearer"
                            }
                        }
                    }
                }
            }
        },
        401: {
            "description": "Authentication failed - invalid credentials",
            "content": {
                "application/json": {
                    "examples": {
                        "wrong_password": {
                            "summary": "Wrong password",
                            "value": {"detail": "Incorrect username or password"}
                        },
                        "user_not_found": {
                            "summary": "User doesn't exist",
                            "value": {"detail": "Incorrect username or password"}
                        }
                    }
                }
            }
        },
        400: {
            "description": "User account is inactive",
            "content": {
                "application/json": {
                    "example": {"detail": "Inactive user"}
                }
            }
        },
        422: {
            "description": "Validation error - missing or invalid fields",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "username"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and obtain JWT access token.

    This OAuth2-compatible endpoint accepts username and password credentials
    via form data and returns a JWT Bearer token for accessing protected endpoints.

    **Authentication Flow:**
    1. Submit username and password as form data (application/x-www-form-urlencoded)
    2. Server validates credentials against database
    3. Server checks if user account is active
    4. Server generates JWT token with 30-minute expiration
    5. Token is returned and should be stored by client

    **Token Usage:**
    Include the token in subsequent requests using the Authorization header:
    ```
    Authorization: Bearer <your_access_token>
    ```

    **Example with cURL:**
    ```bash
    curl -X POST "http://localhost:8000/auth/login" \\
         -H "Content-Type: application/x-www-form-urlencoded" \\
         -d "username=admin&password=changeme"
    ```

    **Example with Python requests:**
    ```python
    import requests

    response = requests.post(
        "http://localhost:8000/auth/login",
        data={"username": "admin", "password": "changeme"}
    )
    token = response.json()["access_token"]
    ```

    **Security Notes:**
    - Tokens expire after 30 minutes (default)
    - Both wrong username and wrong password return the same error to prevent username enumeration
    - Inactive user accounts cannot authenticate

    Args:
        form_data: OAuth2 form containing username and password
        db: Database session (injected)

    Returns:
        Token: JWT access token and token type

    Raises:
        HTTPException 401: Invalid username or password
        HTTPException 400: User account is inactive
        HTTPException 422: Validation error (missing fields)
    """
    # Find user by username
    user = db.query(User).filter(User.username == form_data.username).first()

    # Verify user exists and password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Create access token
    access_token_expires = timedelta(minutes=AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "role": user.role.value
        },
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserResponse,
    responses={
        200: {
            "description": "Successfully retrieved user information",
            "content": {
                "application/json": {
                    "examples": {
                        "admin_user": {
                            "summary": "Admin user profile",
                            "value": {
                                "username": "admin",
                                "email": "admin@art.oem",
                                "id": 1,
                                "role": "admin",
                                "is_active": True,
                                "created_at": "2025-01-15T10:30:00Z",
                                "updated_at": "2025-01-15T10:30:00Z"
                            }
                        },
                        "public_user": {
                            "summary": "Public user profile",
                            "value": {
                                "username": "john_doe",
                                "email": "john@example.com",
                                "id": 42,
                                "role": "public",
                                "is_active": True,
                                "created_at": "2025-01-20T14:45:00Z",
                                "updated_at": "2025-01-20T14:45:00Z"
                            }
                        }
                    }
                }
            }
        },
        401: {
            "description": "Authentication required or token invalid",
            "content": {
                "application/json": {
                    "examples": {
                        "missing_token": {
                            "summary": "No token provided",
                            "value": {"detail": "Not authenticated"}
                        },
                        "invalid_token": {
                            "summary": "Invalid or expired token",
                            "value": {"detail": "Could not validate credentials"}
                        }
                    }
                }
            }
        }
    }
)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get authenticated user's profile information.

    Returns detailed information about the currently authenticated user based on
    the JWT token provided in the Authorization header. This endpoint is useful
    for retrieving user profile data and verifying that authentication is working.

    **Required Header:**
    ```
    Authorization: Bearer <your_access_token>
    ```

    **Example with cURL:**
    ```bash
    curl -X GET "http://localhost:8000/auth/me" \\
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```

    **Example with Python requests:**
    ```python
    import requests

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("http://localhost:8000/auth/me", headers=headers)
    user_info = response.json()
    print(f"Logged in as: {user_info['username']} ({user_info['role']})")
    ```

    **Example with JavaScript fetch:**
    ```javascript
    const response = await fetch('http://localhost:8000/auth/me', {
        headers: {
            'Authorization': `Bearer ${accessToken}`
        }
    });
    const userInfo = await response.json();
    console.log(`Logged in as: ${userInfo.username}`);
    ```

    **Use Cases:**
    - Verify token is still valid
    - Retrieve current user's profile
    - Check user's role for client-side authorization
    - Display user information in UI

    Args:
        current_user: Authenticated user (automatically injected from JWT token)

    Returns:
        UserResponse: Current user's profile information

    Raises:
        HTTPException 401: Missing or invalid authentication token
    """
    return current_user


@router.post(
    "/logout",
    responses={
        200: {
            "description": "Successfully logged out",
            "content": {
                "application/json": {
                    "example": {"message": "Successfully logged out"}
                }
            }
        }
    }
)
async def logout():
    """
    Logout endpoint (client-side token management).

    **Important:** This API uses stateless JWT tokens, which means the server does not
    track active sessions. Logout is primarily handled on the client side by discarding
    the token. This endpoint exists for API completeness and semantic clarity.

    **How to Properly Logout:**

    1. **Client-Side (Recommended):**
       - Delete the token from your storage (localStorage, sessionStorage, cookies, memory)
       - Clear the Authorization header from future requests
       - Redirect user to login page

    2. **Example with JavaScript:**
    ```javascript
    // Logout function
    function logout() {
        localStorage.removeItem('access_token');
        // Optional: Call this endpoint for logging purposes
        fetch('http://localhost:8000/auth/logout', { method: 'POST' });
        window.location.href = '/login';
    }
    ```

    3. **Example with Python:**
    ```python
    # Simply stop using the token
    access_token = None
    # Optional: Call this endpoint
    requests.post('http://localhost:8000/auth/logout')
    ```

    **Future Enhancement - Token Blacklisting:**

    For additional security, this endpoint could be extended to implement token blacklisting:
    - Store invalidated tokens in a blacklist (Redis or database)
    - Check blacklist before validating tokens
    - Automatically clean expired tokens from blacklist
    - Useful for immediate token revocation in security incidents

    **Security Best Practices:**
    - Always clear tokens on logout
    - Use short token expiration times (default: 30 minutes)
    - Store tokens securely (avoid localStorage for sensitive apps)
    - Consider implementing refresh tokens for better UX
    - Implement token blacklisting for high-security applications

    Returns:
        dict: Success message confirming logout

    Notes:
        This endpoint does not require authentication. It can be called
        with or without a valid token.
    """
    return {"message": "Successfully logged out"}

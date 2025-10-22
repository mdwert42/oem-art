# Testing TODO

## Authentication System Tests - ✅ COMPLETED (70/70 tests passing - 100%)

### 1. Auth Utilities Tests (`test_auth_utils.py`) - ✅ ALL PASSING
- [x] Test password hashing
- [x] Test password verification (correct password)
- [x] Test password verification (incorrect password)
- [x] Test JWT token creation
- [x] Test JWT token decoding (valid token)
- [x] Test JWT token decoding (invalid token)
- [x] Test JWT token decoding (expired token)
- [x] Test JWT token with user data (username, user_id, role)

### 2. Auth Endpoints Tests (`test_auth_endpoints.py`) - ✅ ALL PASSING
- [x] Test POST /auth/login with valid credentials
- [x] Test POST /auth/login with invalid username
- [x] Test POST /auth/login with invalid password
- [x] Test POST /auth/login with inactive user
- [x] Test GET /auth/me with valid token
- [x] Test GET /auth/me with invalid token
- [x] Test POST /auth/logout

### 3. Auth Dependencies Tests (`test_auth_dependencies.py`) - ✅ ALL PASSING
- [x] Test get_current_user with valid token
- [x] Test get_current_user with invalid token
- [x] Test get_current_user with expired token
- [x] Test get_current_active_user with active user
- [x] Test get_current_active_user with inactive user
- [x] Test require_admin with admin user
- [x] Test require_admin with public user
- [x] Test require_admin without authentication

### 4. User Model Tests (`test_user_model.py`) - ✅ ALL PASSING
- [x] Test user creation
- [x] Test user with admin role
- [x] Test user with public role
- [x] Test unique username constraint
- [x] Test unique email constraint
- [x] Test user timestamps (created_at, updated_at)
- [x] Test user is_active default value
- [x] Test user role default value (public)

### 5. Integration Tests (`test_auth_integration.py`) - ✅ ALL PASSING
- [x] Test full admin login flow (login → get token → access /auth/me)
- [x] Test full public user flow
- [x] Test accessing admin-only endpoint as admin (success)
- [x] Test accessing admin-only endpoint as public user (forbidden)
- [x] Test token expiration and re-login
- [x] Test concurrent user sessions (FIXED with time.sleep(1))
- [x] Test SQL injection attempt (FIXED with StaticPool)
- [x] Test special characters in password (FIXED with StaticPool)

## Test Setup Requirements - ✅ COMPLETED

### Fixtures Needed
- [x] Test database (SQLite in-memory or test database)
- [x] Test client (FastAPI TestClient)
- [x] Sample users (admin user, public user, inactive user)
- [x] Authentication headers helper

### Test Configuration
- [x] Separate test configuration (test database, test JWT secret)
- [x] Database cleanup between tests
- [x] Mock external dependencies if any

## Known Issues to Fix

### Critical (blocking tests) - ✅ ALL RESOLVED
- [x] ~~Fix "no such table: users" errors~~ - FIXED with StaticPool configuration
- [x] ~~Fix token determinism~~ - FIXED with time.sleep(1) in test

### Library/Dependency Issues - ✅ RESOLVED
- [x] ~~Fixed bcrypt/passlib compatibility issue (downgraded bcrypt to 4.0.1)~~
- [x] ~~Added email-validator to requirements.txt~~

### Test Suite Cleanup - ✅ COMPLETED (2025-10-22)
- [x] Removed duplicate `test_multiple_logins_same_user` from endpoints (covered in integration)
- [x] Removed duplicate `test_login_then_access_me` from endpoints (covered in integration)
- [x] Removed duplicate `test_get_me_without_token` from endpoints (covered in integration)

### Code Quality Issues (Non-blocking)
- [ ] Fix SQLAlchemy deprecation: `declarative_base()` -> `sqlalchemy.orm.declarative_base()` in app/database.py:31
- [ ] Fix FastAPI deprecation: Replace `@app.on_event("startup")` with lifespan event handlers in app/main.py:26
- [ ] Consider: Python 3.13 will remove `crypt` module (passlib dependency warning)

## Future Tests (Post-MVP)

### User Management Tests
- [ ] Test user registration
- [ ] Test password change
- [ ] Test user profile update
- [ ] Test user deactivation

### API Integration Tests
- [ ] Test Instagram API integration
- [ ] Test Facebook API integration
- [ ] Test Shopify API integration

### Performance Tests
- [ ] Test authentication under load
- [ ] Test concurrent login attempts
- [ ] Test token generation performance

## Notes
- Use pytest as the test framework (already in requirements.txt)
- Use FastAPI's TestClient for endpoint testing
- Consider using pytest fixtures for database setup/teardown
- Aim for >80% code coverage on auth module
- Use factories or fixtures for creating test data

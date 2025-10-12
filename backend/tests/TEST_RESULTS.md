# Test Results Summary

## Overall Stats
- **Total Tests**: 73
- **Passed**: 23 (31.5%)
- **Failed**: 21 (28.8%)
- **Errors**: 29 (39.7%)

## Failures by Category

### 1. Password Hashing Tests (4 failures)
All password hashing tests are failing with ValidationError on email field:
- `test_hash_password`
- `test_verify_password_correct`
- `test_verify_password_incorrect`
- `test_verify_password_case_sensitive`

**Root Cause**: The User model has email validation but test users aren't being created with valid email addresses in some cases, or there's an issue with password hashing itself.

### 2. User Model Tests (21 failures)
All user model creation tests failing:
- All tests in `TestUserCreation`
- All tests in `TestUserConstraints`
- All tests in `TestUserDefaults`
- All tests in `TestUserTimestamps`
- All tests in `TestUserRepresentation`

**Root Cause**: ValidationError on User model - likely email validation or missing required fields.

### 3. Auth Dependencies Tests (8 errors)
Tests that use fixtures with actual User objects:
- Tests using `admin_user` fixture
- Tests using `inactive_user` fixture

**Root Cause**: Cascading from fixture creation failures due to User model validation.

### 4. Auth Endpoints Tests (10 errors + 1 failure)
Most endpoint tests failing:
- Login tests with user fixtures
- /auth/me tests with auth headers
- Integration flow tests

**Root Cause**: Cascading from fixture failures. The one unique failure is `test_login_with_invalid_username` which might be a real issue.

### 5. Auth Integration Tests (10 errors + 2 failures)
Similar pattern - tests depending on user fixtures.

Unique failures:
- `test_sql_injection_attempt_in_login`
- `test_special_characters_in_password`

## Tests That ARE Passing (23)

### Auth Dependencies (3 passing)
- ✓ `test_get_current_user_with_invalid_token`
- ✓ `test_get_current_user_with_nonexistent_username`
- ✓ `test_get_current_user_with_token_missing_username`
- ✓ `test_require_admin_checks_both_active_and_role`

### Auth Utils - JWT Tests (7 passing)
All JWT token tests pass:
- ✓ `test_create_access_token_basic`
- ✓ `test_create_access_token_with_expiration`
- ✓ `test_create_access_token_includes_user_data`
- ✓ `test_decode_valid_token`
- ✓ `test_decode_invalid_token`
- ✓ `test_decode_expired_token`
- ✓ `test_decode_token_with_wrong_secret`
- ✓ `test_decode_token_missing_username`
- ✓ `test_decode_token_with_partial_data`

### Auth Endpoints (8 passing)
Tests that don't require user fixtures:
- ✓ `test_login_missing_username`
- ✓ `test_login_missing_password`
- ✓ `test_login_empty_credentials`
- ✓ `test_get_me_with_invalid_token`
- ✓ `test_get_me_without_token`
- ✓ `test_get_me_with_malformed_header`
- ✓ `test_logout`
- ✓ `test_logout_without_token`

### Auth Integration (1 passing)
- ✓ `test_unauthenticated_user_cannot_access_protected_endpoint`

## Primary Issue

The main issue appears to be with **User fixture creation**. Almost all failures trace back to fixtures that create User objects. This suggests:

1. **Email validation issue**: The Pydantic schema might require valid email format
2. **Missing required fields**: Something required isn't being provided
3. **Database/ORM issue**: SQLAlchemy model vs Pydantic schema mismatch

## What Works

- JWT token creation and validation (9/9 tests pass)
- Endpoint validation for missing/malformed requests (8 tests pass)
- Token authentication rejection for invalid/missing tokens (3 tests pass)

## Next Steps

Need to investigate:
1. User model schema validation requirements
2. Fixture setup in `tests/conftest.py` - specifically the `admin_user`, `public_user`, and `inactive_user` fixtures
3. Check if there's a mismatch between SQLAlchemy model and Pydantic schemas

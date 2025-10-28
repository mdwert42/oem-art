# Artwork Management System - Comprehensive Unit Test Plan

## Overview

This document outlines a comprehensive unit test plan for the artwork management system. Tests are organized by component and follow the existing auth test patterns.

**Target Test Coverage:** 90%+
**Test Framework:** pytest, pytest-asyncio, httpx
**Pattern:** Follow existing auth test structure in `tests/auth/`

---

## Test Organization

```
tests/pieces/
├── __init__.py
├── test_piece_model.py           # Database model tests
├── test_piece_schemas.py         # Pydantic schema validation
├── test_piece_endpoints.py       # API endpoint tests
├── test_piece_photos.py          # Photo upload/management
├── test_piece_tags.py            # Tag management
├── test_piece_filtering.py       # List/filter/search functionality
├── test_image_processing.py      # Image processor unit tests
├── test_storage_service.py       # Storage abstraction tests
└── test_piece_integration.py     # Full workflow integration tests
```

---

## 1. Model Tests (`test_piece_model.py`)

### TestPieceCreation
- `test_create_basic_art_piece` - Create minimal art piece
- `test_create_commercial_piece_with_inventory` - Create commercial item with inventory
- `test_create_piece_with_all_fields` - Create with all optional fields
- `test_piece_defaults` - Verify default values (type=ART, status=AVAILABLE, etc.)
- `test_piece_requires_title` - Ensure title is required
- `test_piece_requires_brief_description` - Ensure brief description required
- `test_piece_created_by_foreign_key` - Verify user relationship

### TestPieceRelationships
- `test_piece_to_photos_relationship` - Verify photos relationship
- `test_piece_to_tags_relationship` - Verify tags relationship
- `test_piece_to_comments_relationship` - Verify comments relationship
- `test_piece_to_creator_relationship` - Verify creator relationship
- `test_cascade_delete_photos` - Deleting piece deletes photos
- `test_cascade_delete_tags` - Deleting piece deletes tags
- `test_cascade_delete_comments` - Deleting piece deletes comments

### TestPiecePhoto
- `test_create_piece_photo` - Create photo record
- `test_photo_requires_piece_id` - FK constraint enforced
- `test_photo_requires_stored_filename` - Filename required
- `test_photo_display_order_default` - Default order is 0
- `test_photos_ordered_by_display_order` - Photos returned in correct order
- `test_stored_filename_unique` - Unique constraint on stored filename

### TestPieceTag
- `test_create_tag` - Create tag
- `test_tag_stored_lowercase` - Tags normalized to lowercase
- `test_multiple_tags_per_piece` - One piece can have many tags
- `test_same_tag_multiple_pieces` - Same tag on different pieces
- `test_tag_name_max_length` - 50 character limit enforced

### TestPieceComment
- `test_create_comment` - Create comment (stub model)
- `test_comment_approval_default_false` - Default unapproved
- `test_comment_relationships` - Both piece and user relationships

### TestPieceEnums
- `test_piece_type_enum_values` - ART and COMMERCIAL only
- `test_availability_status_enum_values` - All 4 statuses valid
- `test_invalid_piece_type_rejected` - Invalid type raises error
- `test_invalid_availability_status_rejected` - Invalid status raises error

### TestPieceValidation
- `test_title_max_length_200` - Title length constraint
- `test_brief_description_max_length_500` - Brief description constraint
- `test_inventory_count_non_negative` - Must be >= 0
- `test_price_non_negative` - Must be >= 0

### TestPieceTimestamps
- `test_created_at_auto_set` - Timestamp set on creation
- `test_updated_at_auto_set` - Timestamp set on creation
- `test_updated_at_changes_on_update` - Timestamp updates on modification

---

## 2. Schema Tests (`test_piece_schemas.py`)

### TestPieceCreateSchema
- `test_piece_create_minimal` - Valid with required fields only
- `test_piece_create_with_tags` - Tags array accepted
- `test_piece_create_with_all_fields` - All fields valid
- `test_piece_create_title_too_short` - Min 1 character enforced
- `test_piece_create_title_too_long` - Max 200 characters enforced
- `test_piece_create_brief_too_short` - Min 1 character enforced
- `test_piece_create_brief_too_long` - Max 500 characters enforced
- `test_piece_create_invalid_type` - Invalid piece_type rejected
- `test_piece_create_negative_inventory` - Negative inventory rejected
- `test_piece_create_negative_price` - Negative price rejected
- `test_piece_create_invalid_status` - Invalid availability_status rejected

### TestPieceUpdateSchema
- `test_piece_update_all_fields_optional` - Empty update valid
- `test_piece_update_partial` - Only provided fields validated
- `test_piece_update_title_validation` - Title length validated
- `test_piece_update_negative_values_rejected` - Negative inventory/price rejected

### TestPieceResponseSchema
- `test_piece_response_from_model` - from_attributes works
- `test_piece_response_includes_relationships` - Photos and tags included
- `test_piece_response_includes_timestamps` - Timestamps included
- `test_piece_response_json_serialization` - Serializes to JSON correctly

### TestPieceListResponseSchema
- `test_list_response_structure` - Contains items, total, page, etc.
- `test_list_response_empty` - Works with empty list
- `test_list_response_pagination_fields` - All pagination fields present

### TestPiecePhotoSchemas
- `test_photo_response_from_model` - from_attributes works
- `test_photo_includes_all_paths` - original, medium, thumbnail paths
- `test_photo_display_order_non_negative` - Order >= 0

### TestPieceTagSchemas
- `test_tag_create_valid` - Tag name 1-50 chars
- `test_tag_create_too_long` - Max 50 characters enforced
- `test_tag_create_empty` - Empty tag rejected
- `test_tag_response_from_model` - from_attributes works

### TestSchemaExamples
- `test_all_schemas_have_examples` - OpenAPI examples present
- `test_examples_validate` - Examples pass validation

---

## 3. Endpoint Tests (`test_piece_endpoints.py`)

### TestCreatePieceEndpoint
- `test_create_piece_as_admin` - Admin can create
- `test_create_piece_with_tags` - Tags created automatically
- `test_create_piece_as_public_user` - 403 Forbidden
- `test_create_piece_unauthenticated` - 401 Unauthorized
- `test_create_piece_missing_title` - 422 Validation error
- `test_create_piece_missing_brief_description` - 422 Validation error
- `test_create_piece_invalid_type` - 422 Validation error
- `test_create_piece_negative_inventory` - 422 Validation error
- `test_create_piece_returns_201` - Correct status code
- `test_create_piece_returns_full_object` - Response includes ID, timestamps

### TestGetPieceEndpoint
- `test_get_piece_public_access` - No auth required
- `test_get_piece_includes_photos` - Photos in response
- `test_get_piece_includes_tags` - Tags in response
- `test_get_piece_not_found` - 404 for nonexistent ID
- `test_get_piece_invalid_id` - 422 for invalid ID format

### TestListPiecesEndpoint
- `test_list_pieces_public_access` - No auth required
- `test_list_pieces_default_pagination` - Page 1, size 20
- `test_list_pieces_custom_pagination` - Custom page/size
- `test_list_pieces_max_page_size` - Max 100 enforced
- `test_list_pieces_returns_total_count` - Total field accurate
- `test_list_pieces_returns_total_pages` - Calculated correctly
- `test_list_pieces_empty_result` - Works with no pieces
- `test_list_pieces_ordered_by_created_at_desc` - Newest first

### TestUpdatePieceEndpoint
- `test_update_piece_as_admin` - Admin can update
- `test_update_piece_partial` - Partial update works
- `test_update_piece_full` - Full update works
- `test_update_piece_as_public_user` - 403 Forbidden
- `test_update_piece_unauthenticated` - 401 Unauthorized
- `test_update_piece_not_found` - 404 for nonexistent
- `test_update_piece_invalid_data` - 422 for invalid data
- `test_update_piece_updates_timestamp` - updated_at changes

### TestDeletePieceEndpoint
- `test_delete_piece_as_admin` - Admin can delete
- `test_delete_piece_returns_204` - No content status
- `test_delete_piece_as_public_user` - 403 Forbidden
- `test_delete_piece_unauthenticated` - 401 Unauthorized
- `test_delete_piece_not_found` - 404 for nonexistent
- `test_delete_piece_cascade_deletes_photos` - Photos deleted
- `test_delete_piece_cascade_deletes_tags` - Tags deleted
- `test_delete_piece_removes_from_database` - Can't retrieve after

---

## 4. Photo Tests (`test_piece_photos.py`)

### TestPhotoUploadEndpoint
- `test_upload_photo_as_admin` - Admin can upload
- `test_upload_photo_jpeg` - JPEG accepted
- `test_upload_photo_png` - PNG accepted
- `test_upload_photo_webp` - WebP accepted
- `test_upload_photo_as_public_user` - 403 Forbidden
- `test_upload_photo_unauthenticated` - 401 Unauthorized
- `test_upload_photo_to_nonexistent_piece` - 404 for bad piece_id
- `test_upload_photo_invalid_format` - 400 for unsupported format
- `test_upload_photo_too_large` - 400 for > 10MB
- `test_upload_photo_corrupted` - 400 for corrupted file
- `test_upload_photo_with_display_order` - Custom order accepted
- `test_upload_photo_returns_201` - Correct status code
- `test_upload_photo_returns_paths` - All 3 paths in response
- `test_upload_photo_returns_metadata` - Size, mime_type, etc.

### TestPhotoFileGeneration
- `test_upload_creates_original` - Original file created
- `test_upload_creates_medium` - Medium file created
- `test_upload_creates_thumbnail` - Thumbnail file created
- `test_original_max_size_3000` - Max 3000x3000
- `test_medium_max_size_1200` - Max 1200x1200
- `test_thumbnail_max_size_300` - Max 300x300
- `test_aspect_ratio_preserved` - All versions keep aspect ratio
- `test_files_stored_with_uuid` - UUID-based filenames

### TestPhotoDeleteEndpoint
- `test_delete_photo_as_admin` - Admin can delete
- `test_delete_photo_returns_204` - No content status
- `test_delete_photo_as_public_user` - 403 Forbidden
- `test_delete_photo_unauthenticated` - 401 Unauthorized
- `test_delete_photo_not_found` - 404 for nonexistent
- `test_delete_photo_wrong_piece` - 404 if photo not on piece
- `test_delete_photo_removes_files` - All 3 files deleted
- `test_delete_photo_removes_from_database` - Record deleted

### TestMultiplePhotos
- `test_upload_multiple_photos_to_piece` - Multiple uploads work
- `test_photos_ordered_by_display_order` - Correct ordering
- `test_update_photo_display_order` - Order can be changed
- `test_piece_with_no_photos` - Empty photos array valid

---

## 5. Tag Tests (`test_piece_tags.py`)

### TestAddTagEndpoint
- `test_add_tag_as_admin` - Admin can add tag
- `test_add_tag_lowercase_stored` - Tag normalized to lowercase
- `test_add_tag_whitespace_trimmed` - Whitespace removed
- `test_add_tag_as_public_user` - 403 Forbidden
- `test_add_tag_unauthenticated` - 401 Unauthorized
- `test_add_tag_to_nonexistent_piece` - 404 for bad piece_id
- `test_add_tag_empty_name` - 422 validation error
- `test_add_tag_too_long` - 422 for > 50 chars
- `test_add_duplicate_tag` - Multiple same tags allowed (or handle uniqueness)

### TestRemoveTagEndpoint
- `test_remove_tag_as_admin` - Admin can remove
- `test_remove_tag_returns_204` - No content status
- `test_remove_tag_as_public_user` - 403 Forbidden
- `test_remove_tag_unauthenticated` - 401 Unauthorized
- `test_remove_tag_not_found` - 404 for nonexistent
- `test_remove_tag_wrong_piece` - 404 if tag not on piece
- `test_remove_tag_from_database` - Record deleted

### TestGetAllTagsEndpoint
- `test_get_all_tags_public_access` - No auth required
- `test_get_all_tags_unique` - No duplicates
- `test_get_all_tags_sorted` - Alphabetically sorted
- `test_get_all_tags_empty` - Empty array when no tags
- `test_get_all_tags_across_pieces` - Tags from all pieces

### TestTagsWithPieces
- `test_create_piece_with_tags` - Tags created with piece
- `test_multiple_pieces_same_tag` - Tag reusability
- `test_piece_multiple_tags` - Multiple tags per piece
- `test_delete_piece_deletes_tags` - Cascade delete

---

## 6. Filtering Tests (`test_piece_filtering.py`)

### TestFilterByType
- `test_filter_by_type_art` - piece_type=art
- `test_filter_by_type_commercial` - piece_type=commercial
- `test_filter_by_invalid_type` - Invalid type ignored or error

### TestFilterByAvailability
- `test_filter_by_available` - availability=available
- `test_filter_by_sold` - availability=sold
- `test_filter_by_reserved` - availability=reserved
- `test_filter_by_unlisted` - availability=unlisted

### TestFilterByTag
- `test_filter_by_single_tag` - tag=landscape
- `test_filter_by_tag_case_insensitive` - Tag matching ignores case
- `test_filter_by_nonexistent_tag` - Returns empty
- `test_filter_shows_pieces_with_multiple_tags` - Correct results

### TestSearch
- `test_search_in_title` - Finds by title
- `test_search_in_brief_description` - Finds by brief description
- `test_search_in_full_description` - Finds by full description
- `test_search_case_insensitive` - Case doesn't matter
- `test_search_partial_match` - Substring matching
- `test_search_no_results` - Empty result valid

### TestCombinedFilters
- `test_filter_type_and_tag` - Multiple filters work together
- `test_filter_type_and_search` - Type + search
- `test_filter_tag_and_search` - Tag + search
- `test_all_filters_combined` - Type + availability + tag + search

### TestPagination
- `test_pagination_first_page` - page=1
- `test_pagination_second_page` - page=2
- `test_pagination_last_page` - Last page partial results
- `test_pagination_beyond_last_page` - Empty results
- `test_pagination_total_count_accurate` - Total doesn't change
- `test_pagination_with_filters` - Pagination + filters

---

## 7. Image Processing Tests (`test_image_processing.py`)

### TestImageValidation
- `test_validate_jpeg` - Valid JPEG passes
- `test_validate_png` - Valid PNG passes
- `test_validate_webp` - Valid WebP passes
- `test_validate_rejects_gif` - GIF rejected
- `test_validate_rejects_bmp` - BMP rejected
- `test_validate_rejects_corrupted` - Corrupted image rejected
- `test_validate_max_size_10mb` - 10MB limit enforced
- `test_validate_custom_max_size` - Custom limit works

### TestImageProcessing
- `test_process_creates_three_versions` - Original, medium, thumbnail
- `test_process_returns_dimensions` - Original dimensions returned
- `test_process_converts_to_jpeg` - All output as JPEG
- `test_process_raises_on_unsupported_format` - ValueError for bad format
- `test_process_raises_on_corrupted` - IOError for corrupted

### TestImageResizing
- `test_resize_maintains_aspect_ratio` - Aspect ratio preserved
- `test_resize_original_max_3000` - Original <= 3000x3000
- `test_resize_medium_max_1200` - Medium <= 1200x1200
- `test_resize_thumbnail_max_300` - Thumbnail <= 300x300
- `test_resize_smaller_image_not_upscaled` - Small images not enlarged
- `test_resize_portrait_vs_landscape` - Both orientations work

### TestEXIFHandling
- `test_exif_orientation_corrected` - Image rotated correctly
- `test_exif_orientation_1_no_change` - Normal orientation unchanged
- `test_exif_orientation_6_rotated_90` - 90° rotation applied
- `test_exif_orientation_3_rotated_180` - 180° rotation applied
- `test_exif_orientation_8_rotated_270` - 270° rotation applied
- `test_missing_exif_handled` - No error if no EXIF data

### TestMetadataStripping
- `test_metadata_stripped_from_output` - EXIF removed
- `test_gps_data_removed` - Location data removed
- `test_camera_info_removed` - Camera model removed

### TestRGBConversion
- `test_rgba_to_rgb_white_background` - Transparency handled
- `test_la_to_rgb` - Grayscale+alpha handled
- `test_palette_mode_converted` - Palette images converted
- `test_grayscale_to_rgb` - Grayscale converted

### TestQualitySettings
- `test_thumbnail_quality_85` - Correct quality applied
- `test_medium_quality_90` - Correct quality applied
- `test_original_quality_92` - Correct quality applied

---

## 8. Storage Service Tests (`test_storage_service.py`)

### TestLocalStorageInit
- `test_local_storage_creates_base_dir` - Base directory created
- `test_local_storage_custom_path` - Custom base path works
- `test_local_storage_absolute_path_resolved` - Path resolved correctly

### TestSaveFile
- `test_save_file_basic` - File saved successfully
- `test_save_file_with_subdirectory` - Subdirectory created
- `test_save_file_creates_parent_dirs` - Parent dirs auto-created
- `test_save_file_returns_relative_path` - Correct path returned
- `test_save_file_async` - Async operation works
- `test_save_file_raises_on_error` - IOError on failure

### TestDeleteFile
- `test_delete_file_existing` - Returns True for existing file
- `test_delete_file_nonexistent` - Returns False for nonexistent
- `test_delete_file_actually_removes` - File actually deleted
- `test_delete_file_async` - Async operation works
- `test_delete_file_raises_on_permission_error` - IOError on failure

### TestGetURL
- `test_get_url_format` - Returns /uploads/... format
- `test_get_url_with_subdirectory` - Subdirectory in path
- `test_get_url_for_static_serving` - Compatible with StaticFiles

### TestFileExists
- `test_file_exists_true` - Returns True for existing file
- `test_file_exists_false` - Returns False for nonexistent
- `test_file_exists_directory_returns_false` - Directories return False

### TestGetFileSize
- `test_get_file_size_returns_bytes` - Correct size returned
- `test_get_file_size_nonexistent_returns_none` - None for nonexistent
- `test_get_file_size_directory_returns_none` - None for directory

### TestBaseStorageInterface
- `test_base_storage_cannot_instantiate` - Abstract class can't be instantiated
- `test_base_storage_defines_interface` - All methods defined
- `test_subclass_must_implement_all_methods` - Abstract methods enforced

---

## 9. Integration Tests (`test_piece_integration.py`)

### TestCompleteWorkflow
- `test_full_piece_lifecycle` - Create, add photos, add tags, retrieve, update, delete
- `test_multiple_pieces_with_photos` - Multiple pieces independent
- `test_piece_with_multiple_photos_ordered` - Photo ordering maintained
- `test_search_after_creating_multiple_pieces` - Search works with data

### TestPhotoLifecycle
- `test_upload_verify_files_exist` - Files created on upload
- `test_delete_photo_removes_files` - Files removed on delete
- `test_delete_piece_removes_all_photos` - Cascade delete removes files

### TestTagLifecycle
- `test_create_piece_with_tags_filter_by_tag` - End-to-end tag workflow
- `test_add_tag_appears_in_all_tags_list` - Tag list updates
- `test_remove_tag_updates_all_tags_if_last_use` - Tag list maintenance

### TestConcurrency
- `test_concurrent_photo_uploads` - Multiple uploads don't conflict
- `test_concurrent_piece_creation` - Multiple creates work
- `test_concurrent_tag_additions` - Multiple tag adds work

### TestEdgeCases
- `test_piece_with_very_long_description` - TEXT field handles large content
- `test_piece_with_unicode_in_title` - Unicode supported
- `test_piece_with_special_chars_in_tags` - Special characters handled
- `test_upload_image_with_unicode_filename` - Unicode filenames handled

### TestErrorRecovery
- `test_upload_fails_cleanup` - Failed upload doesn't leave orphan files
- `test_database_rollback_on_error` - Transaction rollback works
- `test_partial_photo_upload_cleanup` - Cleanup on processing failure

---

## Test Data Fixtures

Create fixtures in `tests/pieces/conftest.py`:

```python
@pytest.fixture
def sample_piece_data():
    """Minimal piece creation data"""

@pytest.fixture
def full_piece_data():
    """Complete piece creation data"""

@pytest.fixture
def sample_image_bytes():
    """800x600 test image"""

@pytest.fixture
def large_image_bytes():
    """5000x5000 test image for size limits"""

@pytest.fixture
def corrupted_image_bytes():
    """Invalid image data"""

@pytest.fixture
def sample_jpeg():
    """Valid JPEG file"""

@pytest.fixture
def sample_png():
    """Valid PNG file"""

@pytest.fixture
def sample_webp():
    """Valid WebP file"""

@pytest.fixture
def image_with_exif():
    """Image with various EXIF orientations"""
```

---

## Test Execution Strategy

### Phase 1: Unit Tests (Isolated)
1. Models - No API, just SQLAlchemy
2. Schemas - Pydantic validation only
3. Image Processing - Pure function tests
4. Storage Service - Mock filesystem or temp directories

### Phase 2: API Tests (With TestClient)
1. Endpoint tests - One endpoint at a time
2. Photo tests - With actual image uploads
3. Tag tests - Database interactions
4. Filtering tests - Query testing

### Phase 3: Integration Tests
1. Full workflows
2. Cascade behaviors
3. File system verification
4. Error scenarios

---

## Coverage Goals

- **Overall:** 90%+
- **Models:** 95%+ (straightforward CRUD)
- **Schemas:** 95%+ (validation logic)
- **Endpoints:** 90%+ (auth, errors, happy paths)
- **Services:** 95%+ (pure functions, testable)
- **Integration:** 80%+ (representative workflows)

---

## Commands

```bash
# Run all piece tests
pytest tests/pieces/ -v

# Run with coverage
pytest tests/pieces/ --cov=app.models.piece --cov=app.schemas.piece --cov=app.routers.pieces --cov=app.services

# Run specific test file
pytest tests/pieces/test_piece_model.py -v

# Run specific test
pytest tests/pieces/test_piece_model.py::TestPieceCreation::test_create_basic_art_piece -v
```

---

## Priority Order

### High Priority (Core functionality)
1. Model tests - Ensure data integrity
2. Endpoint tests - API contracts
3. Photo upload tests - Core feature

### Medium Priority (Important features)
4. Tag tests - Categorization
5. Filtering tests - Discoverability
6. Image processing - Quality

### Lower Priority (Nice to have)
7. Storage abstraction - Future-proofing
8. Integration tests - Comprehensive coverage
9. Edge cases - Robustness

---

## Estimated Effort

- **Model tests:** ~15 tests, 2-3 hours
- **Schema tests:** ~20 tests, 2-3 hours
- **Endpoint tests:** ~30 tests, 4-5 hours
- **Photo tests:** ~25 tests, 4-5 hours
- **Tag tests:** ~15 tests, 2-3 hours
- **Filtering tests:** ~20 tests, 3-4 hours
- **Image processing:** ~25 tests, 3-4 hours
- **Storage tests:** ~15 tests, 2-3 hours
- **Integration tests:** ~15 tests, 3-4 hours

**Total:** ~180 tests, ~26-34 hours of work

---

## Success Criteria

✅ All tests pass
✅ 90%+ code coverage
✅ All endpoints tested (happy path + errors)
✅ All validations tested
✅ File operations verified
✅ Database relationships verified
✅ Authentication/authorization tested
✅ Edge cases covered

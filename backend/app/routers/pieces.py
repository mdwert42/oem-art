from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
import uuid
from io import BytesIO

from ..database import get_db
from ..models.user import User
from ..models.piece import Piece, PiecePhoto, PieceTag
from ..schemas.piece import (
    PieceCreate,
    PieceUpdate,
    PieceResponse,
    PieceListResponse,
    PiecePhotoResponse,
    PieceTagCreate,
    PieceTagResponse,
)
from ..auth.dependencies import require_admin, get_current_active_user
from ..services.storage.local_storage import LocalStorage
from ..services.image_processing import ImageProcessor

# Initialize services
storage = LocalStorage(base_path="./uploads")
image_processor = ImageProcessor()

router = APIRouter(
    prefix="/pieces",
    tags=["pieces"],
    responses={
        401: {
            "description": "Authentication failed - missing or invalid token",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        },
        403: {
            "description": "Forbidden - admin access required",
            "content": {
                "application/json": {
                    "example": {"detail": "Admin access required"}
                }
            }
        }
    }
)


# ============================================================================
# Piece CRUD Operations
# ============================================================================

@router.post(
    "/",
    response_model=PieceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new piece",
    responses={
        201: {
            "description": "Piece created successfully",
        },
        422: {
            "description": "Validation error - invalid fields",
        }
    }
)
async def create_piece(
    piece_data: PieceCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new artwork piece or commercial item (Admin only).

    This endpoint allows admins to add new items to the portfolio. After creating
    a piece, use the photo upload endpoint to add images.

    **Process:**
    1. Create the piece with title, description, and metadata
    2. Tags are automatically created if they don't exist
    3. Upload photos separately using the `/pieces/{piece_id}/photos` endpoint

    **Example:**
    ```python
    import requests

    # Login first
    token_response = requests.post(
        "http://localhost:8000/auth/login",
        data={"username": "admin", "password": "changeme"}
    )
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create piece
    piece_data = {
        "title": "Mountain Sunset",
        "brief_description": "A vibrant oil painting",
        "full_description": "Detailed description...",
        "piece_type": "art",
        "tags": ["oil-painting", "landscape"]
    }
    response = requests.post(
        "http://localhost:8000/pieces/",
        json=piece_data,
        headers=headers
    )
    piece = response.json()
    ```
    """
    # Create the piece
    db_piece = Piece(
        title=piece_data.title,
        brief_description=piece_data.brief_description,
        full_description=piece_data.full_description,
        piece_type=piece_data.piece_type,
        inventory_count=piece_data.inventory_count,
        allow_custom_requests=piece_data.allow_custom_requests,
        price=piece_data.price,
        availability_status=piece_data.availability_status,
        created_by=current_user.id
    )
    db.add(db_piece)
    db.flush()  # Flush to get the piece ID

    # Create tags
    for tag_name in piece_data.tags:
        tag = PieceTag(
            piece_id=db_piece.id,
            tag_name=tag_name.lower().strip()  # Normalize tags
        )
        db.add(tag)

    db.commit()
    db.refresh(db_piece)

    return db_piece


@router.get(
    "/",
    response_model=PieceListResponse,
    summary="List all pieces",
    responses={
        200: {
            "description": "List of pieces with pagination",
        }
    }
)
async def list_pieces(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    piece_type: Optional[str] = Query(None, description="Filter by piece type (art or commercial)"),
    availability: Optional[str] = Query(None, description="Filter by availability status"),
    tag: Optional[str] = Query(None, description="Filter by tag name"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of pieces (Public access).

    Returns all pieces with their photos and tags. Supports filtering and search.

    **Filters:**
    - `piece_type`: Filter by "art" or "commercial"
    - `availability`: Filter by status (available, sold, reserved, unlisted)
    - `tag`: Filter by specific tag name
    - `search`: Search in title and descriptions

    **Example:**
    ```bash
    # Get all pieces
    curl http://localhost:8000/pieces/

    # Get art pieces only
    curl http://localhost:8000/pieces/?piece_type=art

    # Search for "sunset"
    curl http://localhost:8000/pieces/?search=sunset

    # Filter by tag
    curl http://localhost:8000/pieces/?tag=oil-painting

    # Paginate
    curl http://localhost:8000/pieces/?page=2&page_size=10
    ```
    """
    # Build query
    query = db.query(Piece)

    # Apply filters
    if piece_type:
        query = query.filter(Piece.piece_type == piece_type)

    if availability:
        query = query.filter(Piece.availability_status == availability)

    if tag:
        # Join with tags and filter
        query = query.join(PieceTag).filter(func.lower(PieceTag.tag_name) == tag.lower())

    if search:
        # Search in title and descriptions
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Piece.title.ilike(search_pattern),
                Piece.brief_description.ilike(search_pattern),
                Piece.full_description.ilike(search_pattern)
            )
        )

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    pieces = query.order_by(Piece.created_at.desc()).offset(offset).limit(page_size).all()

    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size

    return PieceListResponse(
        items=pieces,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/{piece_id}",
    response_model=PieceResponse,
    summary="Get a specific piece",
    responses={
        200: {
            "description": "Piece details retrieved successfully",
        },
        404: {
            "description": "Piece not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Piece not found"}
                }
            }
        }
    }
)
async def get_piece(
    piece_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific piece (Public access).

    Returns complete piece information including all photos and tags.

    **Example:**
    ```bash
    curl http://localhost:8000/pieces/1
    ```
    """
    piece = db.query(Piece).filter(Piece.id == piece_id).first()

    if not piece:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Piece not found"
        )

    return piece


@router.patch(
    "/{piece_id}",
    response_model=PieceResponse,
    summary="Update a piece",
    responses={
        200: {
            "description": "Piece updated successfully",
        },
        404: {
            "description": "Piece not found",
        }
    }
)
async def update_piece(
    piece_id: int,
    piece_update: PieceUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update an existing piece (Admin only).

    Only provided fields will be updated. Use PATCH for partial updates.

    **Example:**
    ```python
    import requests

    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "title": "New Title",
        "price": 500.00
    }
    response = requests.patch(
        "http://localhost:8000/pieces/1",
        json=update_data,
        headers=headers
    )
    ```
    """
    piece = db.query(Piece).filter(Piece.id == piece_id).first()

    if not piece:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Piece not found"
        )

    # Update fields that were provided
    update_data = piece_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(piece, field, value)

    db.commit()
    db.refresh(piece)

    return piece


@router.delete(
    "/{piece_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a piece",
    responses={
        204: {
            "description": "Piece deleted successfully",
        },
        404: {
            "description": "Piece not found",
        }
    }
)
async def delete_piece(
    piece_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a piece and all associated data (Admin only).

    This will cascade delete all photos, tags, and comments associated with the piece.
    The actual image files will also be deleted from storage.

    **Warning:** This action cannot be undone!

    **Example:**
    ```bash
    curl -X DELETE http://localhost:8000/pieces/1 \\
         -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    piece = db.query(Piece).filter(Piece.id == piece_id).first()

    if not piece:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Piece not found"
        )

    # Delete all associated photo files from storage
    for photo in piece.photos:
        try:
            await storage.delete_file(photo.file_path.lstrip('/uploads/'))
            if photo.medium_path:
                await storage.delete_file(photo.medium_path.lstrip('/uploads/'))
            if photo.thumbnail_path:
                await storage.delete_file(photo.thumbnail_path.lstrip('/uploads/'))
        except Exception as e:
            # Log error but continue with deletion
            print(f"Error deleting photo files: {e}")

    # Delete piece (cascade will handle photos, tags, comments)
    db.delete(piece)
    db.commit()

    return None


# ============================================================================
# Photo Management
# ============================================================================

@router.post(
    "/{piece_id}/photos",
    response_model=PiecePhotoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a photo for a piece",
    responses={
        201: {
            "description": "Photo uploaded and processed successfully",
        },
        400: {
            "description": "Invalid image file",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_format": {
                            "summary": "Unsupported format",
                            "value": {"detail": "Invalid image: Unsupported format"}
                        },
                        "too_large": {
                            "summary": "File too large",
                            "value": {"detail": "Image size exceeds maximum (10MB)"}
                        }
                    }
                }
            }
        },
        404: {
            "description": "Piece not found",
        }
    }
)
async def upload_piece_photo(
    piece_id: int,
    file: UploadFile = File(..., description="Image file (JPEG, PNG, or WebP, max 10MB)"),
    display_order: int = Query(0, ge=0, description="Display order (0-based, lower shown first)"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Upload and process a photo for a piece (Admin only).

    The image will be automatically processed to generate:
    - Optimized original (max 3000x3000)
    - Medium version (max 1200x1200)
    - Thumbnail (max 300x300)

    EXIF orientation is corrected and metadata is stripped for privacy.

    **Supported formats:** JPEG, PNG, WebP
    **Maximum size:** 10MB

    **Example with Python:**
    ```python
    import requests

    headers = {"Authorization": f"Bearer {token}"}

    with open("artwork.jpg", "rb") as f:
        files = {"file": ("artwork.jpg", f, "image/jpeg")}
        response = requests.post(
            "http://localhost:8000/pieces/1/photos",
            files=files,
            headers=headers
        )
    ```

    **Example with cURL:**
    ```bash
    curl -X POST http://localhost:8000/pieces/1/photos \\
         -H "Authorization: Bearer YOUR_TOKEN" \\
         -F "file=@/path/to/image.jpg" \\
         -F "display_order=0"
    ```
    """
    # Check if piece exists
    piece = db.query(Piece).filter(Piece.id == piece_id).first()
    if not piece:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Piece not found"
        )

    # Read file data
    file_data = await file.read()

    # Validate image
    is_valid, error_message = image_processor.validate_image(file_data, max_size_mb=10)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    try:
        # Process image
        original, medium, thumbnail, dimensions = image_processor.process_image(file_data)

        # Generate unique filename
        file_extension = "jpg"  # All converted to JPEG
        stored_filename = f"{uuid.uuid4()}.{file_extension}"

        # Save all versions
        original_path = await storage.save_file(
            original,
            stored_filename,
            subdirectory="pieces/originals"
        )

        medium_path = await storage.save_file(
            medium,
            stored_filename,
            subdirectory="pieces/medium"
        )

        thumbnail_path = await storage.save_file(
            thumbnail,
            stored_filename,
            subdirectory="pieces/thumbnails"
        )

        # Create photo record
        photo = PiecePhoto(
            piece_id=piece_id,
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_path=f"/uploads/{original_path}",
            medium_path=f"/uploads/{medium_path}",
            thumbnail_path=f"/uploads/{thumbnail_path}",
            file_size=len(file_data),
            mime_type="image/jpeg",  # All converted to JPEG
            display_order=display_order
        )

        db.add(photo)
        db.commit()
        db.refresh(photo)

        return photo

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process image: {str(e)}"
        )


@router.delete(
    "/{piece_id}/photos/{photo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a photo",
    responses={
        204: {
            "description": "Photo deleted successfully",
        },
        404: {
            "description": "Photo not found",
        }
    }
)
async def delete_photo(
    piece_id: int,
    photo_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a photo from a piece (Admin only).

    This will delete the database record and all image files (original, medium, thumbnail).

    **Example:**
    ```bash
    curl -X DELETE http://localhost:8000/pieces/1/photos/5 \\
         -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    photo = db.query(PiecePhoto).filter(
        PiecePhoto.id == photo_id,
        PiecePhoto.piece_id == piece_id
    ).first()

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )

    # Delete files from storage
    try:
        await storage.delete_file(photo.file_path.lstrip('/uploads/'))
        if photo.medium_path:
            await storage.delete_file(photo.medium_path.lstrip('/uploads/'))
        if photo.thumbnail_path:
            await storage.delete_file(photo.thumbnail_path.lstrip('/uploads/'))
    except Exception as e:
        # Log error but continue with deletion
        print(f"Error deleting photo files: {e}")

    # Delete database record
    db.delete(photo)
    db.commit()

    return None


# ============================================================================
# Tag Management
# ============================================================================

@router.post(
    "/{piece_id}/tags",
    response_model=PieceTagResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a tag to a piece",
    responses={
        201: {
            "description": "Tag added successfully",
        },
        404: {
            "description": "Piece not found",
        }
    }
)
async def add_tag(
    piece_id: int,
    tag_data: PieceTagCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Add a tag to a piece (Admin only).

    Tags are stored in lowercase for consistency. You can use the same tag
    on multiple pieces for categorization.

    **Example:**
    ```python
    import requests

    headers = {"Authorization": f"Bearer {token}"}
    tag_data = {"tag_name": "oil-painting"}
    response = requests.post(
        "http://localhost:8000/pieces/1/tags",
        json=tag_data,
        headers=headers
    )
    ```
    """
    # Check if piece exists
    piece = db.query(Piece).filter(Piece.id == piece_id).first()
    if not piece:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Piece not found"
        )

    # Create tag
    tag = PieceTag(
        piece_id=piece_id,
        tag_name=tag_data.tag_name.lower().strip()
    )

    db.add(tag)
    db.commit()
    db.refresh(tag)

    return tag


@router.delete(
    "/{piece_id}/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a tag from a piece",
    responses={
        204: {
            "description": "Tag removed successfully",
        },
        404: {
            "description": "Tag not found",
        }
    }
)
async def delete_tag(
    piece_id: int,
    tag_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Remove a tag from a piece (Admin only).

    **Example:**
    ```bash
    curl -X DELETE http://localhost:8000/pieces/1/tags/3 \\
         -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    tag = db.query(PieceTag).filter(
        PieceTag.id == tag_id,
        PieceTag.piece_id == piece_id
    ).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    db.delete(tag)
    db.commit()

    return None


@router.get(
    "/tags/all",
    response_model=List[str],
    summary="Get all unique tags",
    responses={
        200: {
            "description": "List of all unique tag names used across all pieces",
        }
    }
)
async def get_all_tags(
    db: Session = Depends(get_db)
):
    """
    Get a list of all unique tags used across all pieces (Public access).

    Useful for creating tag clouds or filter dropdowns.

    **Example:**
    ```bash
    curl http://localhost:8000/pieces/tags/all
    ```

    **Response:**
    ```json
    ["oil-painting", "abstract", "landscape", "portrait", "sculpture"]
    ```
    """
    tags = db.query(PieceTag.tag_name).distinct().order_by(PieceTag.tag_name).all()
    return [tag[0] for tag in tags]

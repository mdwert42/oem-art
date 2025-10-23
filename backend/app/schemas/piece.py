from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class PieceTypeEnum(str, Enum):
    """Type of piece - unique art or commercial inventory"""
    ART = "art"
    COMMERCIAL = "commercial"


class AvailabilityStatusEnum(str, Enum):
    """Availability status for pieces (stub for future e-commerce)"""
    AVAILABLE = "available"
    SOLD = "sold"
    RESERVED = "reserved"
    UNLISTED = "unlisted"


# ============================================================================
# Photo Schemas
# ============================================================================

class PiecePhotoBase(BaseModel):
    """Base photo schema with common fields"""
    display_order: int = Field(
        default=0,
        description="Display order of the photo (0-based, lower numbers shown first)",
        examples=[0, 1, 2],
        ge=0
    )


class PiecePhotoResponse(PiecePhotoBase):
    """
    Schema for photo responses.

    Returned when retrieving piece information. Includes all stored
    photo variants (original, medium, thumbnail) and metadata.
    """
    id: int = Field(
        ...,
        description="Unique identifier for the photo",
        examples=[1, 42]
    )
    piece_id: int = Field(
        ...,
        description="ID of the piece this photo belongs to",
        examples=[1, 10]
    )
    original_filename: str = Field(
        ...,
        description="Original filename from user upload",
        examples=["my-artwork.jpg", "sculpture-front.png"]
    )
    stored_filename: str = Field(
        ...,
        description="UUID-based stored filename",
        examples=["abc123def456.jpg"]
    )
    file_path: str = Field(
        ...,
        description="Path to original size photo",
        examples=["/uploads/pieces/originals/abc123def456.jpg"]
    )
    medium_path: Optional[str] = Field(
        default=None,
        description="Path to medium size photo (1200x1200 max)",
        examples=["/uploads/pieces/medium/abc123def456.jpg"]
    )
    thumbnail_path: Optional[str] = Field(
        default=None,
        description="Path to thumbnail (300x300 max)",
        examples=["/uploads/pieces/thumbnails/abc123def456.jpg"]
    )
    file_size: int = Field(
        ...,
        description="File size in bytes",
        examples=[1024000, 2500000]
    )
    mime_type: str = Field(
        ...,
        description="MIME type of the image",
        examples=["image/jpeg", "image/png"]
    )
    uploaded_at: datetime = Field(
        ...,
        description="Timestamp when photo was uploaded",
        examples=["2025-10-22T14:30:00Z"]
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "piece_id": 5,
                    "original_filename": "sunset-painting.jpg",
                    "stored_filename": "a1b2c3d4-e5f6-7890.jpg",
                    "file_path": "/uploads/pieces/originals/a1b2c3d4-e5f6-7890.jpg",
                    "medium_path": "/uploads/pieces/medium/a1b2c3d4-e5f6-7890.jpg",
                    "thumbnail_path": "/uploads/pieces/thumbnails/a1b2c3d4-e5f6-7890.jpg",
                    "file_size": 2450000,
                    "mime_type": "image/jpeg",
                    "display_order": 0,
                    "uploaded_at": "2025-10-22T14:30:00Z"
                }
            ]
        }
    )


# ============================================================================
# Tag Schemas
# ============================================================================

class PieceTagBase(BaseModel):
    """Base tag schema"""
    tag_name: str = Field(
        ...,
        description="Tag name (will be stored lowercase, 1-50 characters)",
        examples=["oil-painting", "abstract", "portrait", "landscape"],
        min_length=1,
        max_length=50
    )


class PieceTagCreate(PieceTagBase):
    """Schema for creating a tag"""
    pass


class PieceTagResponse(PieceTagBase):
    """
    Schema for tag responses.

    Returned when retrieving piece tags.
    """
    id: int = Field(
        ...,
        description="Unique identifier for the tag",
        examples=[1, 42]
    )
    piece_id: int = Field(
        ...,
        description="ID of the piece this tag belongs to",
        examples=[1, 10]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when tag was created",
        examples=["2025-10-22T14:30:00Z"]
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "piece_id": 5,
                    "tag_name": "oil-painting",
                    "created_at": "2025-10-22T14:30:00Z"
                }
            ]
        }
    )


# ============================================================================
# Piece Schemas
# ============================================================================

class PieceBase(BaseModel):
    """Base piece schema with common fields"""
    title: str = Field(
        ...,
        description="Title of the piece (1-200 characters)",
        examples=["Sunset Over Mountains", "Abstract Composition #5"],
        min_length=1,
        max_length=200
    )
    brief_description: str = Field(
        ...,
        description="Brief description for list views (1-500 characters)",
        examples=["A vibrant oil painting capturing the golden hour"],
        min_length=1,
        max_length=500
    )
    full_description: Optional[str] = Field(
        default=None,
        description="Full rich-text description for detail page",
        examples=["This piece was inspired by a hiking trip to the Rocky Mountains..."]
    )
    piece_type: PieceTypeEnum = Field(
        default=PieceTypeEnum.ART,
        description="Type of piece - 'art' for unique pieces, 'commercial' for inventory items",
        examples=["art", "commercial"]
    )


class PieceCreate(PieceBase):
    """
    Schema for creating a new piece.

    Used by admins to add new artwork or commercial items.
    Photos are uploaded separately after piece creation.
    """
    inventory_count: Optional[int] = Field(
        default=None,
        description="Inventory count (None/1 for unique art, n for commercial items)",
        examples=[None, 1, 50, 100],
        ge=0
    )
    allow_custom_requests: bool = Field(
        default=False,
        description="Whether to allow custom requests for this piece",
        examples=[True, False]
    )
    price: Optional[float] = Field(
        default=None,
        description="Price in USD (stub for future e-commerce)",
        examples=[150.00, 2500.00],
        ge=0
    )
    availability_status: AvailabilityStatusEnum = Field(
        default=AvailabilityStatusEnum.AVAILABLE,
        description="Availability status (stub for future e-commerce)",
        examples=["available", "sold", "reserved", "unlisted"]
    )
    tags: List[str] = Field(
        default=[],
        description="List of tag names to associate with this piece",
        examples=[["oil-painting", "landscape"], ["sculpture", "bronze"]]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Mountain Sunset",
                    "brief_description": "A vibrant oil painting of mountain peaks at sunset",
                    "full_description": "This piece captures the magical golden hour...",
                    "piece_type": "art",
                    "inventory_count": None,
                    "allow_custom_requests": True,
                    "price": None,
                    "availability_status": "available",
                    "tags": ["oil-painting", "landscape", "mountains"]
                },
                {
                    "title": "Custom Art Print",
                    "brief_description": "High-quality giclée print of original artwork",
                    "full_description": "Museum-quality reproduction on archival paper",
                    "piece_type": "commercial",
                    "inventory_count": 50,
                    "allow_custom_requests": False,
                    "price": 45.00,
                    "availability_status": "available",
                    "tags": ["print", "reproduction", "limited-edition"]
                }
            ]
        }
    )


class PieceUpdate(BaseModel):
    """
    Schema for updating piece information.

    All fields are optional - only provided fields will be updated.
    Used by admins to modify existing pieces.
    """
    title: Optional[str] = Field(
        default=None,
        description="New title for the piece",
        examples=["Updated Title"],
        min_length=1,
        max_length=200
    )
    brief_description: Optional[str] = Field(
        default=None,
        description="New brief description",
        examples=["Updated brief description"],
        min_length=1,
        max_length=500
    )
    full_description: Optional[str] = Field(
        default=None,
        description="New full description"
    )
    piece_type: Optional[PieceTypeEnum] = Field(
        default=None,
        description="New piece type"
    )
    inventory_count: Optional[int] = Field(
        default=None,
        description="New inventory count",
        ge=0
    )
    allow_custom_requests: Optional[bool] = Field(
        default=None,
        description="Update custom request setting"
    )
    price: Optional[float] = Field(
        default=None,
        description="New price",
        ge=0
    )
    availability_status: Optional[AvailabilityStatusEnum] = Field(
        default=None,
        description="New availability status"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "New Title",
                    "price": 350.00
                },
                {
                    "availability_status": "sold",
                    "inventory_count": 0
                }
            ]
        }
    )


class PieceResponse(PieceBase):
    """
    Schema for piece responses.

    Returned by API endpoints when retrieving piece information.
    Includes all piece data plus related photos and tags.
    """
    id: int = Field(
        ...,
        description="Unique identifier for the piece",
        examples=[1, 42]
    )
    piece_type: PieceTypeEnum = Field(
        ...,
        description="Type of piece"
    )
    inventory_count: Optional[int] = Field(
        default=None,
        description="Current inventory count"
    )
    allow_custom_requests: bool = Field(
        ...,
        description="Whether custom requests are allowed"
    )
    price: Optional[float] = Field(
        default=None,
        description="Price in USD"
    )
    availability_status: AvailabilityStatusEnum = Field(
        ...,
        description="Current availability status"
    )
    created_by: int = Field(
        ...,
        description="User ID of the creator (admin who added it)",
        examples=[1]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when piece was created",
        examples=["2025-10-22T14:30:00Z"]
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when piece was last updated",
        examples=["2025-10-22T16:45:00Z"]
    )
    photos: List[PiecePhotoResponse] = Field(
        default=[],
        description="Photos associated with this piece, ordered by display_order"
    )
    tags: List[PieceTagResponse] = Field(
        default=[],
        description="Tags associated with this piece"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 5,
                    "title": "Mountain Sunset",
                    "brief_description": "A vibrant oil painting of mountain peaks at sunset",
                    "full_description": "This piece captures the magical golden hour...",
                    "piece_type": "art",
                    "inventory_count": None,
                    "allow_custom_requests": True,
                    "price": None,
                    "availability_status": "available",
                    "created_by": 1,
                    "created_at": "2025-10-22T14:30:00Z",
                    "updated_at": "2025-10-22T14:30:00Z",
                    "photos": [
                        {
                            "id": 1,
                            "piece_id": 5,
                            "original_filename": "sunset.jpg",
                            "stored_filename": "abc123.jpg",
                            "file_path": "/uploads/pieces/originals/abc123.jpg",
                            "medium_path": "/uploads/pieces/medium/abc123.jpg",
                            "thumbnail_path": "/uploads/pieces/thumbnails/abc123.jpg",
                            "file_size": 2450000,
                            "mime_type": "image/jpeg",
                            "display_order": 0,
                            "uploaded_at": "2025-10-22T14:35:00Z"
                        }
                    ],
                    "tags": [
                        {
                            "id": 1,
                            "piece_id": 5,
                            "tag_name": "oil-painting",
                            "created_at": "2025-10-22T14:30:00Z"
                        },
                        {
                            "id": 2,
                            "piece_id": 5,
                            "tag_name": "landscape",
                            "created_at": "2025-10-22T14:30:00Z"
                        }
                    ]
                }
            ]
        }
    )


class PieceListResponse(BaseModel):
    """
    Schema for paginated list of pieces.

    Used by list endpoints to return multiple pieces with pagination metadata.
    """
    items: List[PieceResponse] = Field(
        ...,
        description="List of pieces in this page"
    )
    total: int = Field(
        ...,
        description="Total number of pieces matching the query",
        examples=[42, 100]
    )
    page: int = Field(
        ...,
        description="Current page number (1-based)",
        examples=[1, 2, 3]
    )
    page_size: int = Field(
        ...,
        description="Number of items per page",
        examples=[20, 50]
    )
    total_pages: int = Field(
        ...,
        description="Total number of pages",
        examples=[5, 10]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "items": [],
                    "total": 42,
                    "page": 1,
                    "page_size": 20,
                    "total_pages": 3
                }
            ]
        }
    )

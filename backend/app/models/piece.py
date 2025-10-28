from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum, ForeignKey, Numeric, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum


class PieceType(str, enum.Enum):
    """Type of piece - unique art or commercial inventory"""
    ART = "art"
    COMMERCIAL = "commercial"


class AvailabilityStatus(str, enum.Enum):
    """Availability status for pieces (stub for future e-commerce)"""
    AVAILABLE = "available"
    SOLD = "sold"
    RESERVED = "reserved"
    UNLISTED = "unlisted"


class Piece(Base):
    """
    Core piece model - represents both unique art pieces and commercial inventory.

    Shared infrastructure with different handling:
    - ART pieces: Unique items with full showcase (inventory_count typically None or 1)
    - COMMERCIAL pieces: Mass-produced items with inventory tracking

    Future features stubbed: price, availability, comments
    """
    __tablename__ = "pieces"

    # Core fields
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    brief_description = Column(String(500), nullable=False)  # For list views
    full_description = Column(Text, nullable=True)  # Rich text for detail page
    piece_type = Column(Enum(PieceType), nullable=False, default=PieceType.ART, index=True)

    # Commercial-specific
    inventory_count = Column(Integer, nullable=True)  # None for unique art, n for commercial
    allow_custom_requests = Column(Boolean, default=False, nullable=False)

    # Future e-commerce fields (stub)
    price = Column(Numeric(10, 2), nullable=True)  # Decimal for currency
    availability_status = Column(
        Enum(AvailabilityStatus),
        default=AvailabilityStatus.AVAILABLE,
        nullable=False,
        index=True
    )

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    photos = relationship("PiecePhoto", back_populates="piece", cascade="all, delete-orphan", order_by="PiecePhoto.display_order")
    tags = relationship("PieceTag", back_populates="piece", cascade="all, delete-orphan")
    comments = relationship("PieceComment", back_populates="piece", cascade="all, delete-orphan")
    creator = relationship("User")

    def __repr__(self):
        return f"<Piece(id={self.id}, title='{self.title}', type={self.piece_type})>"


class PiecePhoto(Base):
    """
    Photos associated with a piece. Supports multiple photos per piece.
    Stores paths for original, medium, and thumbnail versions.
    """
    __tablename__ = "piece_photos"

    id = Column(Integer, primary_key=True, index=True)
    piece_id = Column(Integer, ForeignKey("pieces.id", ondelete="CASCADE"), nullable=False, index=True)

    # File information
    original_filename = Column(String(255), nullable=False)  # User's original filename
    stored_filename = Column(String(255), nullable=False, unique=True)  # UUID-based filename
    file_path = Column(String(500), nullable=False)  # Path to original
    medium_path = Column(String(500), nullable=True)  # Path to medium version
    thumbnail_path = Column(String(500), nullable=True)  # Path to thumbnail

    # Metadata
    file_size = Column(Integer, nullable=False)  # Bytes
    mime_type = Column(String(50), nullable=False)  # e.g., image/jpeg
    display_order = Column(Integer, nullable=False, default=0)  # For ordering photos
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship
    piece = relationship("Piece", back_populates="photos")

    # Index for efficient ordering
    __table_args__ = (
        Index('ix_piece_photos_piece_order', 'piece_id', 'display_order'),
    )

    def __repr__(self):
        return f"<PiecePhoto(id={self.id}, piece_id={self.piece_id}, filename='{self.stored_filename}')>"


class PieceTag(Base):
    """
    Free-form tags for pieces. Enables flexible categorization and search.
    Many tags can be associated with one piece.
    """
    __tablename__ = "piece_tags"

    id = Column(Integer, primary_key=True, index=True)
    piece_id = Column(Integer, ForeignKey("pieces.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_name = Column(String(50), nullable=False, index=True)  # Stored lowercase for consistency
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship
    piece = relationship("Piece", back_populates="tags")

    # Index for tag searches
    __table_args__ = (
        Index('ix_piece_tags_tag_name_lower', func.lower(tag_name)),
    )

    def __repr__(self):
        return f"<PieceTag(id={self.id}, piece_id={self.piece_id}, tag='{self.tag_name}')>"


class PieceComment(Base):
    """
    User comments on pieces (stub for future feature).
    Model exists but no endpoints implemented yet.
    Includes approval workflow for moderation.
    """
    __tablename__ = "piece_comments"

    id = Column(Integer, primary_key=True, index=True)
    piece_id = Column(Integer, ForeignKey("pieces.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment_text = Column(Text, nullable=False)
    is_approved = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    piece = relationship("Piece", back_populates="comments")
    user = relationship("User")

    def __repr__(self):
        return f"<PieceComment(id={self.id}, piece_id={self.piece_id}, user_id={self.user_id})>"

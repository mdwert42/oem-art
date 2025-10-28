"""
Tests for Piece model.

Tests piece creation, constraints, defaults, and relationships.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.piece import Piece, PiecePhoto, PieceTag, PieceType, AvailabilityStatus
from app.models.user import User, UserRole
from app.auth.utils import hash_password


class TestPieceCreation:
    """Tests for basic piece creation."""

    def test_create_basic_art_piece(self, test_db: Session):
        """Test creating a minimal art piece with required fields only."""
        # Create a user first (required for created_by FK)
        user = User(
            username="artist",
            email="artist@example.com",
            hashed_password=hash_password("password"),
            role=UserRole.ADMIN
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Create basic art piece
        piece = Piece(
            title="Test Artwork",
            brief_description="A beautiful test piece",
            piece_type=PieceType.ART,
            created_by=user.id
        )
        test_db.add(piece)
        test_db.commit()
        test_db.refresh(piece)

        # Verify piece was created
        assert piece.id is not None
        assert piece.title == "Test Artwork"
        assert piece.brief_description == "A beautiful test piece"
        assert piece.piece_type == PieceType.ART
        assert piece.created_by == user.id
        assert piece.full_description is None  # Optional field
        assert piece.inventory_count is None  # Optional for art
        assert piece.allow_custom_requests is False  # Default
        assert piece.price is None  # Optional
        assert piece.availability_status == AvailabilityStatus.AVAILABLE  # Default

    def test_create_commercial_piece_with_inventory(self, test_db: Session):
        """Test creating a commercial piece with inventory count."""
        # Create user
        user = User(
            username="seller",
            email="seller@example.com",
            hashed_password=hash_password("password"),
            role=UserRole.ADMIN
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Create commercial piece with inventory
        piece = Piece(
            title="Art Print",
            brief_description="High-quality print",
            piece_type=PieceType.COMMERCIAL,
            inventory_count=50,
            price=45.00,
            created_by=user.id
        )
        test_db.add(piece)
        test_db.commit()
        test_db.refresh(piece)

        assert piece.id is not None
        assert piece.piece_type == PieceType.COMMERCIAL
        assert piece.inventory_count == 50
        assert piece.price == 45.00

    def test_create_piece_with_all_fields(self, test_db: Session):
        """Test creating a piece with all optional fields populated."""
        # Create user
        user = User(
            username="creator",
            email="creator@example.com",
            hashed_password=hash_password("password"),
            role=UserRole.ADMIN
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Create piece with all fields
        piece = Piece(
            title="Complete Piece",
            brief_description="Brief description here",
            full_description="This is a much longer, detailed description of the artwork...",
            piece_type=PieceType.ART,
            inventory_count=1,
            allow_custom_requests=True,
            price=2500.00,
            availability_status=AvailabilityStatus.RESERVED,
            created_by=user.id
        )
        test_db.add(piece)
        test_db.commit()
        test_db.refresh(piece)

        assert piece.id is not None
        assert piece.title == "Complete Piece"
        assert piece.brief_description == "Brief description here"
        assert piece.full_description == "This is a much longer, detailed description of the artwork..."
        assert piece.piece_type == PieceType.ART
        assert piece.inventory_count == 1
        assert piece.allow_custom_requests is True
        assert piece.price == 2500.00
        assert piece.availability_status == AvailabilityStatus.RESERVED
        assert piece.created_by == user.id

    def test_piece_defaults(self, test_db: Session):
        """Test that piece default values are set correctly."""
        # Create user
        user = User(
            username="defaultuser",
            email="default@example.com",
            hashed_password=hash_password("password"),
            role=UserRole.ADMIN
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Create piece with minimal fields
        piece = Piece(
            title="Default Test",
            brief_description="Testing defaults",
            created_by=user.id
        )
        test_db.add(piece)
        test_db.commit()
        test_db.refresh(piece)

        # Check defaults
        assert piece.piece_type == PieceType.ART  # Default
        assert piece.availability_status == AvailabilityStatus.AVAILABLE  # Default
        assert piece.allow_custom_requests is False  # Default
        assert piece.inventory_count is None  # Not set
        assert piece.price is None  # Not set
        assert piece.full_description is None  # Not set

    def test_piece_requires_title(self, test_db: Session):
        """Test that title is required (cannot be null)."""
        # Create user
        user = User(
            username="requser",
            email="req@example.com",
            hashed_password=hash_password("password"),
            role=UserRole.ADMIN
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Try to create piece without title
        piece = Piece(
            brief_description="No title provided",
            created_by=user.id
        )
        test_db.add(piece)

        # Should raise IntegrityError
        with pytest.raises(IntegrityError):
            test_db.commit()

    def test_piece_requires_brief_description(self, test_db: Session):
        """Test that brief_description is required (cannot be null)."""
        # Create user
        user = User(
            username="briefuser",
            email="brief@example.com",
            hashed_password=hash_password("password"),
            role=UserRole.ADMIN
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Try to create piece without brief_description
        piece = Piece(
            title="No Brief Description",
            created_by=user.id
        )
        test_db.add(piece)

        # Should raise IntegrityError
        with pytest.raises(IntegrityError):
            test_db.commit()

    def test_piece_created_by_foreign_key(self, test_db: Session):
        """Test that created_by references a valid user (relationship exists)."""
        # Create a user
        user = User(
            username="fkuser",
            email="fk@example.com",
            hashed_password=hash_password("password"),
            role=UserRole.ADMIN
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Create piece with valid user_id
        piece = Piece(
            title="Valid FK",
            brief_description="Testing FK relationship",
            created_by=user.id
        )
        test_db.add(piece)
        test_db.commit()
        test_db.refresh(piece)

        # Verify the relationship works
        assert piece.created_by == user.id
        assert piece.creator.id == user.id
        assert piece.creator.username == "fkuser"

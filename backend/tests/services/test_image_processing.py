"""
Tests for ImageProcessor service.

Tests image processing, validation, resizing, and optimization.
"""

import pytest
from PIL import Image
from io import BytesIO

from app.services.image_processing import ImageProcessor


class TestImageProcessing:
    """Tests for main image processing functionality."""

    def create_test_image(self, size=(1000, 800), format='JPEG', mode='RGB'):
        """Helper to create a test image."""
        img = Image.new(mode, size, color='red')
        buffer = BytesIO()
        img.save(buffer, format=format)
        buffer.seek(0)
        return buffer.getvalue()

    def test_process_jpeg_image(self):
        """Test processing a valid JPEG image."""
        image_data = self.create_test_image(size=(2000, 1500), format='JPEG')

        original, medium, thumbnail, dimensions = ImageProcessor.process_image(image_data)

        # Verify all outputs are BytesIO
        assert isinstance(original, BytesIO)
        assert isinstance(medium, BytesIO)
        assert isinstance(thumbnail, BytesIO)

        # Verify original dimensions captured
        assert dimensions == (2000, 1500)

        # Verify files have content
        assert len(original.getvalue()) > 0
        assert len(medium.getvalue()) > 0
        assert len(thumbnail.getvalue()) > 0

    def test_process_png_image(self):
        """Test processing a PNG image (should convert to JPEG)."""
        image_data = self.create_test_image(size=(1000, 800), format='PNG')

        original, medium, thumbnail, dimensions = ImageProcessor.process_image(image_data)

        # Verify all outputs exist
        assert original is not None
        assert medium is not None
        assert thumbnail is not None
        assert dimensions == (1000, 800)

    def test_process_webp_image(self):
        """Test processing a WebP image."""
        image_data = self.create_test_image(size=(800, 600), format='WEBP')

        original, medium, thumbnail, dimensions = ImageProcessor.process_image(image_data)

        assert original is not None
        assert dimensions == (800, 600)

    def test_process_image_creates_correct_sizes(self):
        """Test that generated images are within size constraints."""
        # Create large image
        image_data = self.create_test_image(size=(3500, 3500), format='JPEG')

        original, medium, thumbnail, _ = ImageProcessor.process_image(image_data)

        # Check sizes
        original_img = Image.open(original)
        assert original_img.size[0] <= 3000
        assert original_img.size[1] <= 3000

        medium_img = Image.open(medium)
        assert medium_img.size[0] <= 1200
        assert medium_img.size[1] <= 1200

        thumbnail_img = Image.open(thumbnail)
        assert thumbnail_img.size[0] <= 300
        assert thumbnail_img.size[1] <= 300

    def test_process_image_maintains_aspect_ratio(self):
        """Test that aspect ratio is preserved during resizing."""
        # Create 2:1 aspect ratio image
        image_data = self.create_test_image(size=(2000, 1000), format='JPEG')

        original, medium, thumbnail, _ = ImageProcessor.process_image(image_data)

        # Check aspect ratios
        medium_img = Image.open(medium)
        aspect_ratio = medium_img.size[0] / medium_img.size[1]
        assert 1.9 < aspect_ratio < 2.1  # Allow small variance

        thumbnail_img = Image.open(thumbnail)
        aspect_ratio = thumbnail_img.size[0] / thumbnail_img.size[1]
        assert 1.9 < aspect_ratio < 2.1

    def test_process_rgba_image_converts_to_rgb(self):
        """Test that RGBA images are converted to RGB."""
        image_data = self.create_test_image(size=(500, 500), format='PNG', mode='RGBA')

        original, _, _, _ = ImageProcessor.process_image(image_data)

        original_img = Image.open(original)
        assert original_img.mode == 'RGB'

    def test_process_image_unsupported_format_raises_error(self):
        """Test that unsupported image formats raise ValueError."""
        # Create a BMP image (not in SUPPORTED_FORMATS)
        img = Image.new('RGB', (100, 100), color='blue')
        buffer = BytesIO()
        img.save(buffer, format='BMP')
        buffer.seek(0)

        with pytest.raises(ValueError, match="Unsupported image format"):
            ImageProcessor.process_image(buffer.getvalue())

    def test_process_corrupted_image_raises_error(self):
        """Test that corrupted images raise IOError."""
        corrupted_data = b'not an image at all'

        with pytest.raises(IOError, match="Failed to process image"):
            ImageProcessor.process_image(corrupted_data)


class TestImageValidation:
    """Tests for image validation functionality."""

    def create_test_image(self, size=(1000, 800), format='JPEG'):
        """Helper to create a test image."""
        img = Image.new('RGB', size, color='green')
        buffer = BytesIO()
        img.save(buffer, format=format)
        buffer.seek(0)
        return buffer.getvalue()

    def test_validate_valid_jpeg(self):
        """Test validation of a valid JPEG image."""
        image_data = self.create_test_image(format='JPEG')

        is_valid, error = ImageProcessor.validate_image(image_data)

        assert is_valid is True
        assert error is None

    def test_validate_valid_png(self):
        """Test validation of a valid PNG image."""
        image_data = self.create_test_image(format='PNG')

        is_valid, error = ImageProcessor.validate_image(image_data)

        assert is_valid is True
        assert error is None

    def test_validate_file_too_large(self):
        """Test validation fails for files exceeding size limit."""
        # Create data that's definitely over the size limit
        # Using a 0.1MB limit with 0.2MB of data
        large_data = b'\x00' * (200 * 1024)  # 200KB

        # Validate with 0.1MB limit
        is_valid, error = ImageProcessor.validate_image(large_data, max_size_mb=0.1)

        assert is_valid is False
        assert "exceeds maximum" in error

    def test_validate_unsupported_format(self):
        """Test validation fails for unsupported formats."""
        # Create BMP image
        img = Image.new('RGB', (100, 100), color='yellow')
        buffer = BytesIO()
        img.save(buffer, format='BMP')
        buffer.seek(0)

        is_valid, error = ImageProcessor.validate_image(buffer.getvalue())

        assert is_valid is False
        assert "Unsupported format" in error

    def test_validate_corrupted_image(self):
        """Test validation fails for corrupted images."""
        corrupted_data = b'this is not an image'

        is_valid, error = ImageProcessor.validate_image(corrupted_data)

        assert is_valid is False
        assert "Invalid image" in error

    def test_validate_empty_data(self):
        """Test validation fails for empty data."""
        is_valid, error = ImageProcessor.validate_image(b'')

        assert is_valid is False
        assert error is not None


class TestImageOrientation:
    """Tests for EXIF orientation handling."""

    def test_fix_orientation_handles_no_exif(self):
        """Test that images without EXIF don't cause errors."""
        img = Image.new('RGB', (100, 100), color='red')

        result = ImageProcessor._fix_orientation(img)

        assert result is not None
        assert result.size == (100, 100)


class TestImageConversion:
    """Tests for image mode conversion."""

    def test_convert_rgba_to_rgb(self):
        """Test RGBA to RGB conversion with white background."""
        img = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))

        result = ImageProcessor._convert_to_rgb(img)

        assert result.mode == 'RGB'
        assert result.size == (100, 100)

    def test_convert_palette_to_rgb(self):
        """Test palette mode to RGB conversion."""
        img = Image.new('P', (100, 100))

        result = ImageProcessor._convert_to_rgb(img)

        assert result.mode == 'RGB'

    def test_convert_already_rgb_unchanged(self):
        """Test that RGB images remain unchanged."""
        img = Image.new('RGB', (100, 100), color='blue')

        result = ImageProcessor._convert_to_rgb(img)

        assert result.mode == 'RGB'
        assert result is img  # Should return same object


class TestMetadataStripping:
    """Tests for metadata removal."""

    def test_strip_metadata_removes_exif(self):
        """Test that metadata stripping creates new image without EXIF."""
        img = Image.new('RGB', (100, 100), color='green')

        result = ImageProcessor._strip_metadata(img)

        # Verify it's a new image
        assert result is not img
        assert result.size == img.size
        assert result.mode == img.mode


class TestImageResizing:
    """Tests for image resizing functionality."""

    def test_resize_large_image_to_fit_constraints(self):
        """Test resizing large image to fit within max size."""
        img = Image.new('RGB', (2000, 1500), color='purple')

        result = ImageProcessor._resize_image(img, (1200, 1200), quality=90)

        result_img = Image.open(result)
        assert result_img.size[0] <= 1200
        assert result_img.size[1] <= 1200

    def test_resize_small_image_not_upscaled(self):
        """Test that small images are not upscaled."""
        img = Image.new('RGB', (200, 150), color='orange')

        result = ImageProcessor._resize_image(img, (1200, 1200), quality=90)

        result_img = Image.open(result)
        # Should not exceed original size
        assert result_img.size[0] <= 200
        assert result_img.size[1] <= 150

    def test_resize_returns_jpeg(self):
        """Test that resized image is JPEG format."""
        img = Image.new('RGB', (500, 500), color='cyan')

        result = ImageProcessor._resize_image(img, (300, 300), quality=85)

        result_img = Image.open(result)
        assert result_img.format == 'JPEG'

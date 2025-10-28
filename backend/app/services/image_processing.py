from PIL import Image, ImageOps, ExifTags
from io import BytesIO
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Image processing service for artwork photos.

    Handles:
    - Thumbnail generation (300x300)
    - Medium size generation (1200x1200)
    - Original optimization
    - EXIF orientation correction
    - Metadata stripping for privacy
    """

    # Size configurations
    THUMBNAIL_SIZE = (300, 300)
    MEDIUM_SIZE = (1200, 1200)
    MAX_ORIGINAL_SIZE = (3000, 3000)  # Max size for originals

    # Quality settings
    THUMBNAIL_QUALITY = 85
    MEDIUM_QUALITY = 90
    ORIGINAL_QUALITY = 92

    # Supported formats
    SUPPORTED_FORMATS = {'JPEG', 'PNG', 'WEBP'}
    OUTPUT_FORMAT = 'JPEG'  # Convert everything to JPEG for consistency

    @staticmethod
    def _fix_orientation(image: Image.Image) -> Image.Image:
        """
        Auto-rotate image based on EXIF orientation tag.

        Args:
            image: PIL Image object

        Returns:
            Image: Correctly oriented image
        """
        try:
            # Use ImageOps.exif_transpose which handles all EXIF orientations
            image = ImageOps.exif_transpose(image)
        except Exception as e:
            logger.warning(f"Could not fix image orientation: {e}")

        return image

    @staticmethod
    def _strip_metadata(image: Image.Image) -> Image.Image:
        """
        Strip EXIF and other metadata from image for privacy.

        Args:
            image: PIL Image object

        Returns:
            Image: Image without metadata
        """
        # Create a new image without metadata
        data = list(image.getdata())
        image_without_exif = Image.new(image.mode, image.size)
        image_without_exif.putdata(data)
        return image_without_exif

    @staticmethod
    def _convert_to_rgb(image: Image.Image) -> Image.Image:
        """
        Convert image to RGB mode (required for JPEG).

        Args:
            image: PIL Image object

        Returns:
            Image: RGB mode image
        """
        if image.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            return background
        elif image.mode != 'RGB':
            return image.convert('RGB')
        return image

    @staticmethod
    def _resize_image(
        image: Image.Image,
        max_size: Tuple[int, int],
        quality: int
    ) -> BytesIO:
        """
        Resize image to fit within max_size while maintaining aspect ratio.

        Args:
            image: PIL Image object
            max_size: Maximum dimensions (width, height)
            quality: JPEG quality (1-100)

        Returns:
            BytesIO: Resized image as bytes
        """
        # Calculate thumbnail size maintaining aspect ratio
        image.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Convert to RGB for JPEG
        image = ImageProcessor._convert_to_rgb(image)

        # Save to BytesIO
        output = BytesIO()
        image.save(output, format=ImageProcessor.OUTPUT_FORMAT, quality=quality, optimize=True)
        output.seek(0)
        return output

    @classmethod
    def process_image(
        cls,
        image_data: bytes
    ) -> Tuple[BytesIO, BytesIO, BytesIO, Tuple[int, int]]:
        """
        Process an uploaded image and generate all required versions.

        Args:
            image_data: Raw image bytes

        Returns:
            Tuple containing:
            - original: Optimized original image
            - medium: Medium-sized version (1200x1200 max)
            - thumbnail: Thumbnail version (300x300 max)
            - dimensions: Original image dimensions (width, height)

        Raises:
            ValueError: If image format is not supported
            IOError: If image cannot be processed
        """
        try:
            # Open image from bytes
            image = Image.open(BytesIO(image_data))

            # Verify format is supported
            if image.format not in cls.SUPPORTED_FORMATS:
                raise ValueError(
                    f"Unsupported image format: {image.format}. "
                    f"Supported formats: {', '.join(cls.SUPPORTED_FORMATS)}"
                )

            # Store original dimensions
            original_dimensions = image.size

            # Fix orientation based on EXIF
            image = cls._fix_orientation(image)

            # Strip metadata for privacy
            image = cls._strip_metadata(image)

            # Generate thumbnail
            thumbnail_image = image.copy()
            thumbnail = cls._resize_image(
                thumbnail_image,
                cls.THUMBNAIL_SIZE,
                cls.THUMBNAIL_QUALITY
            )

            # Generate medium version
            medium_image = image.copy()
            medium = cls._resize_image(
                medium_image,
                cls.MEDIUM_SIZE,
                cls.MEDIUM_QUALITY
            )

            # Generate optimized original (with max size constraint)
            original_image = image.copy()
            original = cls._resize_image(
                original_image,
                cls.MAX_ORIGINAL_SIZE,
                cls.ORIGINAL_QUALITY
            )

            return original, medium, thumbnail, original_dimensions

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise IOError(f"Failed to process image: {str(e)}")

    @classmethod
    def validate_image(cls, image_data: bytes, max_size_mb: int = 10) -> Tuple[bool, Optional[str]]:
        """
        Validate an image before processing.

        Args:
            image_data: Raw image bytes
            max_size_mb: Maximum file size in megabytes

        Returns:
            Tuple of (is_valid, error_message)
            If valid, error_message is None
        """
        # Check file size
        size_mb = len(image_data) / (1024 * 1024)
        if size_mb > max_size_mb:
            return False, f"Image size ({size_mb:.1f}MB) exceeds maximum ({max_size_mb}MB)"

        # Try to open and verify image
        try:
            image = Image.open(BytesIO(image_data))

            # Verify format
            if image.format not in cls.SUPPORTED_FORMATS:
                return False, f"Unsupported format: {image.format}. Supported: {', '.join(cls.SUPPORTED_FORMATS)}"

            # Verify image is not corrupted
            image.verify()

            return True, None

        except Exception as e:
            return False, f"Invalid image: {str(e)}"

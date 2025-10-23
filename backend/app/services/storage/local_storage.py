import os
import aiofiles
from pathlib import Path
from typing import BinaryIO, Optional
from .base_storage import BaseStorage


class LocalStorage(BaseStorage):
    """
    Local filesystem storage implementation.

    Stores files on the local disk. Suitable for development and small-scale deployments.
    For production with multiple servers, consider GCP Cloud Storage or AWS S3.
    """

    def __init__(self, base_path: str = "./uploads"):
        """
        Initialize local storage.

        Args:
            base_path: Base directory for file storage (relative to project root)
        """
        self.base_path = Path(base_path).resolve()
        # Create base directory if it doesn't exist
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_full_path(self, file_path: str) -> Path:
        """
        Get the full filesystem path from a relative path.

        Args:
            file_path: Relative file path

        Returns:
            Path: Full filesystem path
        """
        return self.base_path / file_path

    async def save_file(
        self,
        file_data: BinaryIO,
        filename: str,
        subdirectory: Optional[str] = None
    ) -> str:
        """
        Save a file to local storage.

        Args:
            file_data: Binary file data to save
            filename: Name to save the file as
            subdirectory: Optional subdirectory (e.g., 'pieces/originals')

        Returns:
            str: Relative path to the saved file

        Raises:
            IOError: If file cannot be saved
        """
        # Construct the relative path
        if subdirectory:
            relative_path = Path(subdirectory) / filename
        else:
            relative_path = Path(filename)

        # Get full filesystem path
        full_path = self._get_full_path(str(relative_path))

        # Create parent directories if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Save the file asynchronously
        try:
            async with aiofiles.open(full_path, 'wb') as f:
                # Read and write in chunks for memory efficiency
                content = file_data.read()
                await f.write(content)

            return str(relative_path)
        except Exception as e:
            raise IOError(f"Failed to save file {filename}: {str(e)}")

    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from local storage.

        Args:
            file_path: Relative path to the file

        Returns:
            bool: True if deleted successfully, False if file doesn't exist
        """
        full_path = self._get_full_path(file_path)

        try:
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception as e:
            raise IOError(f"Failed to delete file {file_path}: {str(e)}")

    async def get_url(self, file_path: str) -> str:
        """
        Get a URL to access the file.

        For local storage, returns a path that can be served by FastAPI's StaticFiles.

        Args:
            file_path: Relative path to the file

        Returns:
            str: URL path for accessing the file (e.g., '/uploads/pieces/originals/file.jpg')
        """
        # In production, this might need to be an absolute URL
        # For now, return a path that FastAPI can serve
        return f"/uploads/{file_path}"

    async def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists in local storage.

        Args:
            file_path: Relative path to check

        Returns:
            bool: True if file exists, False otherwise
        """
        full_path = self._get_full_path(file_path)
        return full_path.exists() and full_path.is_file()

    async def get_file_size(self, file_path: str) -> Optional[int]:
        """
        Get the size of a file in bytes.

        Args:
            file_path: Relative path to the file

        Returns:
            Optional[int]: File size in bytes, or None if file doesn't exist
        """
        full_path = self._get_full_path(file_path)

        if full_path.exists() and full_path.is_file():
            return full_path.stat().st_size
        return None

from abc import ABC, abstractmethod
from typing import BinaryIO, Optional
from pathlib import Path


class BaseStorage(ABC):
    """
    Abstract base class for storage backends.

    Defines the interface that all storage implementations must follow.
    Makes it easy to switch between local filesystem, GCP Cloud Storage,
    AWS S3, or any other storage backend.
    """

    @abstractmethod
    async def save_file(
        self,
        file_data: BinaryIO,
        filename: str,
        subdirectory: Optional[str] = None
    ) -> str:
        """
        Save a file to storage.

        Args:
            file_data: Binary file data to save
            filename: Name to save the file as (should be unique, e.g., UUID-based)
            subdirectory: Optional subdirectory within storage (e.g., 'originals', 'thumbnails')

        Returns:
            str: Path or URL to the saved file

        Raises:
            IOError: If file cannot be saved
        """
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from storage.

        Args:
            file_path: Path or URL to the file to delete

        Returns:
            bool: True if deleted successfully, False otherwise

        Raises:
            IOError: If file cannot be deleted
        """
        pass

    @abstractmethod
    async def get_url(self, file_path: str) -> str:
        """
        Get a URL to access the file.

        For local storage: returns a path that can be served by FastAPI
        For cloud storage: returns a public URL or signed URL

        Args:
            file_path: Path to the file

        Returns:
            str: URL or path to access the file
        """
        pass

    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists in storage.

        Args:
            file_path: Path to check

        Returns:
            bool: True if file exists, False otherwise
        """
        pass

    @abstractmethod
    async def get_file_size(self, file_path: str) -> Optional[int]:
        """
        Get the size of a file in bytes.

        Args:
            file_path: Path to the file

        Returns:
            Optional[int]: File size in bytes, or None if file doesn't exist
        """
        pass

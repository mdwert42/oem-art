"""
Storage service abstraction layer.

Provides a consistent interface for file storage operations,
allowing easy switching between local filesystem and cloud storage (GCP, S3, etc.).
"""

from .base_storage import BaseStorage
from .local_storage import LocalStorage

__all__ = ["BaseStorage", "LocalStorage"]

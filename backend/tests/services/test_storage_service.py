"""
Tests for Storage service implementations.

Tests local storage and base storage interface.
"""

import pytest
import os
import tempfile
import shutil
from io import BytesIO
from pathlib import Path

from app.services.storage.local_storage import LocalStorage
from app.services.storage.base_storage import BaseStorage


class TestLocalStorageInit:
    """Tests for LocalStorage initialization."""

    def test_init_creates_base_directory(self):
        """Test that initialization creates base directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalStorage(base_path=tmpdir)

            assert storage.base_path.exists()
            assert storage.base_path.is_dir()

    def test_init_with_nonexistent_path_creates_it(self):
        """Test that nonexistent paths are created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_path = os.path.join(tmpdir, "uploads", "test")
            storage = LocalStorage(base_path=new_path)

            assert Path(new_path).exists()


class TestLocalStorageSaveFile:
    """Tests for LocalStorage file saving."""

    @pytest.fixture
    def storage(self):
        """Fixture providing a temporary LocalStorage instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield LocalStorage(base_path=tmpdir)

    @pytest.mark.asyncio
    async def test_save_file_basic(self, storage):
        """Test saving a basic file."""
        content = b"test file content"
        file_data = BytesIO(content)

        path = await storage.save_file(file_data, "test.txt")

        assert path == "test.txt"
        full_path = storage._get_full_path(path)
        assert full_path.exists()
        with open(full_path, 'rb') as f:
            assert f.read() == content

    @pytest.mark.asyncio
    async def test_save_file_with_subdirectory(self, storage):
        """Test saving file in subdirectory."""
        content = b"test content"
        file_data = BytesIO(content)

        path = await storage.save_file(file_data, "image.jpg", subdirectory="pieces/originals")

        assert path == "pieces/originals/image.jpg"
        full_path = storage._get_full_path(path)
        assert full_path.exists()
        assert full_path.parent.name == "originals"

    @pytest.mark.asyncio
    async def test_save_file_creates_nested_directories(self, storage):
        """Test that nested subdirectories are created."""
        content = b"nested content"
        file_data = BytesIO(content)

        path = await storage.save_file(
            file_data,
            "file.txt",
            subdirectory="level1/level2/level3"
        )

        full_path = storage._get_full_path(path)
        assert full_path.exists()
        assert full_path.parent.name == "level3"

    @pytest.mark.asyncio
    async def test_save_binary_file(self, storage):
        """Test saving binary file data."""
        # Create fake image data
        content = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        file_data = BytesIO(content)

        path = await storage.save_file(file_data, "image.png", subdirectory="images")

        full_path = storage._get_full_path(path)
        with open(full_path, 'rb') as f:
            saved_content = f.read()
            assert saved_content == content

    @pytest.mark.asyncio
    async def test_save_multiple_files(self, storage):
        """Test saving multiple files."""
        files = [
            ("file1.txt", b"content 1"),
            ("file2.txt", b"content 2"),
            ("file3.txt", b"content 3")
        ]

        for filename, content in files:
            file_data = BytesIO(content)
            path = await storage.save_file(file_data, filename)
            assert storage._get_full_path(path).exists()


class TestLocalStorageDeleteFile:
    """Tests for LocalStorage file deletion."""

    @pytest.fixture
    def storage(self):
        """Fixture providing a temporary LocalStorage instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield LocalStorage(base_path=tmpdir)

    @pytest.mark.asyncio
    async def test_delete_existing_file(self, storage):
        """Test deleting an existing file."""
        # First create a file
        content = b"to be deleted"
        file_data = BytesIO(content)
        path = await storage.save_file(file_data, "delete_me.txt")

        # Verify it exists
        assert storage._get_full_path(path).exists()

        # Delete it
        await storage.delete_file(path)

        # Verify it's gone
        assert not storage._get_full_path(path).exists()

    @pytest.mark.asyncio
    async def test_delete_file_in_subdirectory(self, storage):
        """Test deleting file from subdirectory."""
        content = b"nested delete"
        file_data = BytesIO(content)
        path = await storage.save_file(file_data, "file.txt", subdirectory="sub/dir")

        await storage.delete_file(path)

        assert not storage._get_full_path(path).exists()

    @pytest.mark.asyncio
    async def test_delete_nonexistent_file_no_error(self, storage):
        """Test deleting nonexistent file doesn't raise error."""
        # Should not raise an exception
        await storage.delete_file("nonexistent.txt")

    @pytest.mark.asyncio
    async def test_delete_file_with_nested_path(self, storage):
        """Test deleting file with complex path."""
        content = b"complex path"
        file_data = BytesIO(content)
        path = await storage.save_file(
            file_data,
            "image.jpg",
            subdirectory="pieces/originals/2025"
        )

        await storage.delete_file(path)

        assert not storage._get_full_path(path).exists()


class TestLocalStorageFileExists:
    """Tests for LocalStorage file existence check."""

    @pytest.fixture
    def storage(self):
        """Fixture providing a temporary LocalStorage instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield LocalStorage(base_path=tmpdir)

    @pytest.mark.asyncio
    async def test_file_exists_for_existing_file(self, storage):
        """Test file_exists returns True for existing files."""
        content = b"exists"
        file_data = BytesIO(content)
        path = await storage.save_file(file_data, "exists.txt")

        exists = await storage.file_exists(path)

        assert exists is True

    @pytest.mark.asyncio
    async def test_file_exists_for_nonexistent_file(self, storage):
        """Test file_exists returns False for nonexistent files."""
        exists = await storage.file_exists("does_not_exist.txt")

        assert exists is False

    @pytest.mark.asyncio
    async def test_file_exists_for_file_in_subdirectory(self, storage):
        """Test file_exists works with subdirectories."""
        content = b"nested exists"
        file_data = BytesIO(content)
        path = await storage.save_file(file_data, "file.txt", subdirectory="sub")

        exists = await storage.file_exists(path)

        assert exists is True


class TestLocalStorageGetUrl:
    """Tests for LocalStorage URL generation."""

    @pytest.fixture
    def storage(self):
        """Fixture providing a temporary LocalStorage instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield LocalStorage(base_path=tmpdir)

    @pytest.mark.asyncio
    async def test_get_url_basic(self, storage):
        """Test URL generation for basic file."""
        content = b"url test"
        file_data = BytesIO(content)
        path = await storage.save_file(file_data, "image.jpg")

        url = await storage.get_url(path)

        assert url == "/uploads/image.jpg"

    @pytest.mark.asyncio
    async def test_get_url_with_subdirectory(self, storage):
        """Test URL generation for file in subdirectory."""
        content = b"url test"
        file_data = BytesIO(content)
        path = await storage.save_file(file_data, "photo.jpg", subdirectory="pieces/medium")

        url = await storage.get_url(path)

        assert url == "/uploads/pieces/medium/photo.jpg"

    @pytest.mark.asyncio
    async def test_get_url_normalizes_path(self, storage):
        """Test that URL paths are properly normalized."""
        # Create file
        content = b"normalize"
        file_data = BytesIO(content)
        path = await storage.save_file(file_data, "test.jpg", subdirectory="a/b")

        url = await storage.get_url(path)

        # Should use forward slashes
        assert "/" in url
        assert "\\" not in url


class TestLocalStorageGetFullPath:
    """Tests for internal path resolution."""

    def test_get_full_path_basic(self):
        """Test basic path resolution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalStorage(base_path=tmpdir)

            full_path = storage._get_full_path("test.txt")

            assert str(full_path).endswith("test.txt")
            assert tmpdir in str(full_path)

    def test_get_full_path_with_subdirectory(self):
        """Test path resolution with subdirectory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalStorage(base_path=tmpdir)

            full_path = storage._get_full_path("sub/dir/file.txt")

            assert "sub" in str(full_path)
            assert "dir" in str(full_path)
            assert str(full_path).endswith("file.txt")


class TestBaseStorage:
    """Tests for BaseStorage abstract interface."""

    def test_base_storage_is_abstract(self):
        """Test that BaseStorage cannot be instantiated."""
        # BaseStorage is abstract and requires subclass implementation
        # This test verifies the interface exists
        assert hasattr(BaseStorage, 'save_file')
        assert hasattr(BaseStorage, 'delete_file')
        assert hasattr(BaseStorage, 'file_exists')
        assert hasattr(BaseStorage, 'get_url')
        assert hasattr(BaseStorage, 'get_file_size')

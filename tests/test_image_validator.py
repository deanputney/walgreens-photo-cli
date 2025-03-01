"""Tests for the image validator module."""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from PIL import UnidentifiedImageError

from walgreens_print.image_validator import (
    validate_images,
    _validate_single_image,
    _validate_directory,
    _has_valid_extension,
    _has_valid_filename,
    ImageValidationError,
    ImageBatchValidationError
)


def test_validate_images_file_not_exists():
    """Test validation when file doesn't exist."""
    with patch.object(Path, 'exists', return_value=False):
        with pytest.raises(ImageValidationError, match="Could not find file"):
            validate_images('nonexistent.jpg')


def test_validate_images_single_file():
    """Test validation with a single valid file."""
    with patch.object(Path, 'exists', return_value=True):
        with patch.object(Path, 'is_file', return_value=True):
            with patch.object(Path, 'is_dir', return_value=False):
                with patch('walgreens_print.image_validator._validate_single_image'):
                    result = validate_images('valid.jpg')
                    assert result == ['valid.jpg']


def test_validate_images_directory():
    """Test validation with a valid directory."""
    expected_paths = ['dir/img1.jpg', 'dir/img2.png']
    
    with patch.object(Path, 'exists', return_value=True):
        with patch.object(Path, 'is_file', return_value=False):
            with patch.object(Path, 'is_dir', return_value=True):
                with patch('walgreens_print.image_validator._validate_directory', return_value=expected_paths):
                    result = validate_images('dir')
                    assert result == expected_paths


def test_validate_single_image_invalid_extension():
    """Test validation with invalid file extension."""
    path = MagicMock()
    path.suffix = '.bmp'
    
    with pytest.raises(ImageValidationError, match="not supported"):
        _validate_single_image(path)


def test_validate_single_image_invalid_filename():
    """Test validation with invalid filename characters."""
    path = MagicMock()
    path.suffix = '.jpg'
    path.name = 'bad!file.jpg'
    
    with patch('walgreens_print.image_validator._has_valid_extension', return_value=True):
        with patch('walgreens_print.image_validator._has_valid_filename', return_value=False):
            with pytest.raises(ImageValidationError, match="special characters"):
                _validate_single_image(path)


def test_validate_single_image_corrupted():
    """Test validation with a corrupted image file."""
    path = MagicMock()
    path.suffix = '.jpg'
    path.name = 'valid.jpg'
    
    with patch('walgreens_print.image_validator._has_valid_extension', return_value=True):
        with patch('walgreens_print.image_validator._has_valid_filename', return_value=True):
            with patch('PIL.Image.open', side_effect=UnidentifiedImageError):
                with pytest.raises(ImageValidationError, match="corrupted"):
                    _validate_single_image(path)


def test_validate_directory_too_many_images():
    """Test directory validation with too many images."""
    directory = MagicMock()
    # Create more than 100 mock image paths
    too_many_paths = [Path(f'img{i}.jpg') for i in range(101)]
    
    with patch.object(Path, 'glob', side_effect=lambda pattern: 
                     too_many_paths if pattern.endswith('.jpg') else []):
        with pytest.raises(ImageValidationError, match="Maximum limit is 100"):
            _validate_directory(directory)


def test_validate_directory_no_images():
    """Test directory validation with no images."""
    directory = MagicMock()
    
    with patch.object(Path, 'glob', return_value=[]):
        with pytest.raises(ImageValidationError, match="No JPG or PNG images found"):
            _validate_directory(directory)


def test_validate_directory_with_errors():
    """Test directory validation with some invalid images."""
    directory = MagicMock()
    image_paths = [Path('valid.jpg'), Path('invalid.jpg')]
    
    with patch.object(Path, 'glob', side_effect=lambda pattern: 
                     image_paths if pattern.endswith('.jpg') else []):
        with patch('walgreens_print.image_validator._validate_single_image', 
                   side_effect=[None, ImageValidationError("Test error")]):
            with pytest.raises(ImageBatchValidationError):
                _validate_directory(directory)


def test_has_valid_extension():
    """Test checking for valid file extensions."""
    assert _has_valid_extension(Path('test.jpg')) is True
    assert _has_valid_extension(Path('test.jpeg')) is True
    assert _has_valid_extension(Path('test.png')) is True
    assert _has_valid_extension(Path('test.bmp')) is False
    assert _has_valid_extension(Path('test.txt')) is False


def test_has_valid_filename():
    """Test checking for valid filenames."""
    assert _has_valid_filename(Path('valid.jpg')) is True
    assert _has_valid_filename(Path('valid_name.jpg')) is True
    assert _has_valid_filename(Path('valid-name.jpg')) is True
    assert _has_valid_filename(Path('invalid!.jpg')) is False
    assert _has_valid_filename(Path('invalid .jpg')) is False 
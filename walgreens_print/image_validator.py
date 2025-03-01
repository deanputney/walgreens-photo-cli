"""Image validation module for Walgreens Photo Printing tool."""

import os
import re
from pathlib import Path
from PIL import Image, UnidentifiedImageError


class ImageValidationError(Exception):
    """Exception raised for image validation errors."""
    pass


class ImageBatchValidationError(Exception):
    """Exception raised when multiple image validation errors occur."""
    
    def __init__(self, errors):
        """Initialize with a list of errors."""
        self.errors = errors
        message = "\n".join(str(error) for error in errors)
        super().__init__(message)


def validate_images(path):
    """
    Validate the image(s) at the given path.
    
    Args:
        path: Path to an image file or a directory containing images.
        
    Returns:
        A list of valid image paths.
        
    Raises:
        ImageValidationError: If a single image validation fails.
        ImageBatchValidationError: If multiple validations fail.
    """
    path = Path(path)
    
    if not path.exists():
        raise ImageValidationError(f"Error: Could not find file or directory '{path}'")
    
    if path.is_file():
        # Single file validation
        _validate_single_image(path)
        return [str(path)]
    
    elif path.is_dir():
        # Directory validation
        return _validate_directory(path)
    
    else:
        raise ImageValidationError(f"Error: '{path}' is not a file or directory")


def _validate_single_image(path):
    """Validate a single image file."""
    # Check file extension
    if not _has_valid_extension(path):
        raise ImageValidationError(
            f"Error: Image format '{path.suffix}' is not supported. Please use JPG or PNG"
        )
    
    # Check filename for special characters
    if not _has_valid_filename(path):
        raise ImageValidationError(
            f"Error: File '{path.name}' contains special characters. Please rename the file using only letters, numbers, dashes, and underscores"
        )
    
    # Check if the file is a valid image
    try:
        with Image.open(path) as img:
            # Just opening the image is enough to validate it's readable
            pass
    except (UnidentifiedImageError, IOError):
        raise ImageValidationError(f"Error: Image file '{path}' appears to be corrupted")


def _validate_directory(directory):
    """Validate all images in a directory."""
    # Find all JPG and PNG files
    image_paths = []
    for ext in [".jpg", ".jpeg", ".png"]:
        image_paths.extend(list(directory.glob(f"*{ext}")))
        image_paths.extend(list(directory.glob(f"*{ext.upper()}")))
    
    # Check if too many images
    if len(image_paths) > 100:
        raise ImageValidationError(
            f"Error: Found {len(image_paths)} photos in folder. Maximum limit is 100 photos per order."
        )
    
    if not image_paths:
        raise ImageValidationError(f"Error: No JPG or PNG images found in '{directory}'")
    
    # Validate each image
    errors = []
    valid_paths = []
    
    for img_path in image_paths:
        try:
            _validate_single_image(img_path)
            valid_paths.append(str(img_path))
        except ImageValidationError as e:
            errors.append(e)
    
    if errors:
        raise ImageBatchValidationError(errors)
    
    return valid_paths


def _has_valid_extension(path):
    """Check if the file has a valid image extension."""
    valid_extensions = [".jpg", ".jpeg", ".png"]
    return path.suffix.lower() in valid_extensions


def _has_valid_filename(path):
    """Check if the filename contains only allowed characters."""
    pattern = r'^[a-zA-Z0-9_\-]+\.[a-zA-Z0-9]+$'
    return bool(re.match(pattern, path.name)) 
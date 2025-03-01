"""Utility functions for Walgreens Photo Printing tool."""

import os
import sys
import tempfile
from typing import Dict


class CleanupManager:
    """Manager for cleaning up temporary resources."""
    
    def __init__(self):
        """Initialize the cleanup manager."""
        self.temp_files = []
        self.temp_dirs = []
        self.cleanup_handlers = []
    
    def add_file(self, file_path):
        """Add a file to be cleaned up."""
        if file_path and os.path.exists(file_path):
            self.temp_files.append(file_path)
    
    def add_directory(self, dir_path):
        """Add a directory to be cleaned up."""
        if dir_path and os.path.exists(dir_path):
            self.temp_dirs.append(dir_path)
    
    def add_handler(self, handler):
        """Add a custom cleanup handler function."""
        if callable(handler):
            self.cleanup_handlers.append(handler)
    
    def cleanup(self):
        """Perform cleanup of all temporary resources."""
        # Execute custom handlers
        for handler in self.cleanup_handlers:
            try:
                handler()
            except Exception as e:
                print(f"Warning: Cleanup handler failed: {e}", file=sys.stderr)
        
        # Remove temporary files
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Warning: Failed to remove temporary file {file_path}: {e}", file=sys.stderr)
        
        # Remove temporary directories
        for dir_path in self.temp_dirs:
            try:
                if os.path.exists(dir_path):
                    import shutil
                    shutil.rmtree(dir_path, ignore_errors=True)
            except Exception as e:
                print(f"Warning: Failed to remove temporary directory {dir_path}: {e}", file=sys.stderr)


# Global cleanup manager instance
cleanup_manager = CleanupManager()


def create_temp_file(suffix=None, prefix=None, dir=None):
    """Create a temporary file and register it for cleanup."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, prefix=prefix, dir=dir)
    temp_file.close()
    cleanup_manager.add_file(temp_file.name)
    return temp_file.name


def create_temp_dir(suffix=None, prefix=None, dir=None):
    """Create a temporary directory and register it for cleanup."""
    temp_dir = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
    cleanup_manager.add_directory(temp_dir)
    return temp_dir


def format_success_message(image_paths, order_details):
    """Format a success message for the user."""
    image_count = len(image_paths)
    
    if image_count == 1:
        image_name = os.path.basename(image_paths[0])
        message = f"Successfully submitted {image_name} for printing at Walgreens."
    else:
        message = f"Successfully submitted {image_count} photos for printing at Walgreens."
    
    return f"{message} Order #{order_details['order_number']}. {order_details['pickup_details']}" 


def prepare_image_payload(image_path_or_url: str) -> Dict[str, str]:
    """
    Prepare image payload for Walgreens API.
    
    Args:
        image_path_or_url: Either a local file path or a URL to an already uploaded image
        
    Returns:
        Dict with image URL and quantity
    """
    # If this is already a URL (from a previous upload), just return it
    if image_path_or_url.startswith("http"):
        return {
            "url": image_path_or_url,
            "qty": "1"  # Default quantity is 1
        }
    
    # Otherwise, it's a file path that needs to be uploaded
    # The actual upload will be handled elsewhere
    return {
        "url": image_path_or_url,  # This will be replaced with the uploaded URL
        "qty": "1"
    } 
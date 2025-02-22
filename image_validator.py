# image_validator.py

import os
from pathlib import Path
from PIL import Image

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
MAX_IMAGES = 100
VALID_FILENAME_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")

def is_valid_extension(filename):
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

def is_valid_filename(filename):
    return all(c in VALID_FILENAME_CHARS for c in filename)

def validate_image_file(filepath):
    if not os.path.exists(filepath):
        return f"Error: File does not exist - {filepath}"
    
    if not is_valid_extension(filepath):
        return f"Error: Invalid file extension - {filepath}"
    
    if not is_valid_filename(Path(filepath).name):
        return f"Error: Invalid characters in filename - {filepath}"

    try:
        with Image.open(filepath) as img:
            img.verify()  # Verify that it's a readable image
    except (IOError, SyntaxError) as e:
        return f"Error: File is not a valid image - {filepath} ({e})"
    
    return None

def collect_image_files(input_path):
    if os.path.isdir(input_path):
        images = []
        for root, _, files in os.walk(input_path):
            for file in files:
                filepath = Path(root) / file
                if is_valid_extension(filepath):
                    images.append(filepath)
        
        if len(images) > MAX_IMAGES:
            return f"Error: Too many images. Limit is {MAX_IMAGES}."
        
        return images
    
    elif os.path.isfile(input_path) and is_valid_extension(input_path):
        return [input_path]
    
    else:
        return f"Error: Invalid input path or file extension - {input_path}"

def validate_images(input_path):
    image_files = collect_image_files(input_path)
    
    if isinstance(image_files, str):  # Error message
        return image_files
    
    errors = []
    valid_images = []
    
    for filepath in image_files:
        error = validate_image_file(filepath)
        if error:
            errors.append(error)
        else:
            valid_images.append(filepath)
    
    if errors:
        return "\n".join(errors)
    
    return valid_images

if __name__ == '__main__':
    # Example usage
    input_path = input("Enter the path to an image file or directory: ").strip()
    result = validate_images(input_path)
    print(result)

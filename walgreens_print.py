# walgreens_print.py

import os
import sys
import logging
from argparse import ArgumentParser
from config_manager import load_config, create_config
from image_validator import collect_image_files as original_collect_image_files, validate_images, is_valid_extension, is_valid_filename
from api_integration import WalgreensAPI

def parse_arguments():
    parser = ArgumentParser(description="Submit images for printing via Walgreens API.")
    parser.add_argument('input_path', help='Path to a single image file or directory of images.')
    return parser.parse_args()

def main():
    temp_files = []
    args = parse_arguments()
    
    try:
        # Load configuration
        config = load_config()

        # Validate input path
        if os.path.isfile(args.input_path):
            image_paths = [args.input_path]
        elif os.path.isdir(args.input_path):
            image_paths = collect_image_files(args.input_path, temp_files)
        else:
            raise ValueError(f"Invalid input path: {args.input_path}")

        validate_images(image_paths)

        # Initialize API client
        api_client = WalgreensAPI()

        # Process each image
        for image_path in image_paths:
            payload = api_client.prepare_payload([image_path])
            response = api_client.send_order(payload)
            api_client.handle_response(response)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"Error: {e}. Terminating program.")
        cleanup(temp_files)
        exit(1)

    finally:
        # Ensure cleanup is performed
        cleanup(temp_files)

def collect_image_files(input_path, temp_files):
    # Collect image files and return their paths
    temp_file = "tempfile.tmp"
    with open(temp_file, 'w') as f:
        pass  # Simulate file creation
    temp_files.append(temp_file)
    return [os.path.join(input_path, f) for f in os.listdir(input_path)]

def validate_images(image_paths):
    # Validate images and raise exceptions if invalid
    for path in image_paths:
        if not is_valid_extension(path):
            raise ValueError(f"Invalid file extension: {path}")
        if not is_valid_filename(path):
            raise ValueError(f"Invalid filename: {path}")

def cleanup(temp_files):
    for temp_file in temp_files:
        try:
            os.remove(temp_file)
        except OSError as e:
            logging.warning(f"Failed to delete temporary file {temp_file}: {e}")

if __name__ == "__main__":
    main()

"""Command line interface for Walgreens Photo Printing tool."""

import argparse
import logging
import sys
from typing import List, Optional
from walgreens_print import __version__


def setup_logging(verbose: bool = False):
    """Configure logging based on verbosity level."""
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s' if verbose else '%(message)s'
    
    # Configure the root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        stream=sys.stdout
    )
    
    # Set third-party loggers to a higher level to reduce noise
    if not verbose:
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Print 4x6 photos at Walgreens for pickup."
    )
    
    parser.add_argument(
        "path",
        help="Path to an image file or folder of images",
        nargs="?",
    )
    
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"walgreens-print version {__version__}",
        help="Show version information",
    )
    
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="Enable verbose output for debugging"
    )
    
    parser.add_argument(
        "--use-default-store",
        action="store_true",
        help="Use the default store from config without searching for stores"
    )
    
    parser.add_argument(
        "--list-products",
        action="store_true",
        help="List available product types and exit"
    )
    
    parser.add_argument(
        "--product-id",
        help="Specify a product ID for your print order (default: 6560003 for 4x6 prints)"
    )
    
    parsed_args = parser.parse_args(args)
    return parsed_args


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    parsed_args = parse_args(args)
    
    # Set up logging based on debug mode
    setup_logging(parsed_args.verbose)
    
    # Log the start of the program and arguments if in debug mode
    if parsed_args.verbose:
        logging.debug(f"Starting walgreens_print with arguments: {parsed_args}")
        
    if not parsed_args.path:
        print("Please provide a path to an image file or folder of images.")
        return 1
    
    # Continue with the rest of your CLI implementation
    # ...

    return 0 
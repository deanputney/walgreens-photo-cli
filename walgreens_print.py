import argparse
import sys

def main():
    parser = argparse.ArgumentParser(
        description="Walgreens Photo Printing Tool",
        epilog="Enjoy printing your photos!"
    )
    
    # Add version argument
    parser.add_argument('-v', '--version', action='version', version='walgreens-print version 1.0.0')
    
    # Add positional argument for image file or folder path
    parser.add_argument('path', type=str, help="Path to the image file or folder")
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no arguments are provided, show help text
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    # Placeholder for processing the path argument
    print(f"Processing path: {args.path}")

if __name__ == '__main__':
    main()

# Walgreens Photo Printing CLI

A command-line tool to submit 4x6 photos to Walgreens for printing and pickup.

## Features

- Submit single image files or entire folders of images
- Validate images against Walgreens printing requirements
- Automatically manage API credentials
- Simple, user-friendly feedback
- Support for JPG and PNG formats

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/walgreens-print.git
cd walgreens-print

# Install the package
pip install -e .
```

## Usage

```bash
# Print a single photo
walgreens-print photo.jpg

# Print all photos in a folder
walgreens-print ./vacation-photos/

# Show help
walgreens-print --help

# Show version
walgreens-print --version
```

## Configuration

On first run, the tool will prompt you for your Walgreens API credentials:

- API Key
- Affiliate ID
- Store ID

These credentials are stored in `~/.config/walgreens-print/config.yaml`.

## Requirements

- Python 3.6 or higher
- PyYAML (for configuration)
- Pillow (for image validation)
- Requests (for API communication)

## Error Handling

The tool includes comprehensive error handling for:

- Invalid images
- Network connectivity issues
- API errors
- Partial upload failures

## Testing

Run the tests with pytest:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run tests
pytest
```

## Limitations

- Maximum 100 photos per order
- Supports only JPG and PNG formats
- Photos are printed as 4x6 prints

## Walgreens API Notes

The Walgreens API uses different affiliate IDs for different services:

- PhotoPrints: `photoapi`
- Store Locator: `storesapi`
- RxRefill & Transfer: `rxapi`
- Balance Rewards: `brctest`

This application automatically uses the correct affiliate ID for each API endpoint.

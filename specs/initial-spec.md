# Walgreens Photo Printing CLI

## Command Line Interface

The tool will accept command line arguments rather than using an interactive prompt. Users will provide image paths directly as arguments when running the command.

Example usage:

```bash
walgreens-print path/to/image.jpg
walgreens-print path/to/folder
```

The tool will process up to 100 photos from a single folder. If more than 100 photos are found, it will exit with an error message: "Error: Found 143 photos in folder. Maximum limit is 100 photos per order."

## Help Text

The tool will display help text when run with `-h` or `--help`, or when no arguments are provided:

```
Usage: walgreens-print <path>

Print 4x6 photos at Walgreens for pickup.

Arguments:
  <path>        Path to an image file or folder of images

Options:
  -h, --help     Show this help message
  -v, --version  Show version information

Examples:
  walgreens-print photo.jpg
  walgreens-print ./vacation-photos/

Notes:
  - Supports JPG and PNG formats
  - Maximum 100 photos per order
  - Photos will be printed at the configured Walgreens location
  - First-time use will prompt for API credentials
```

When run with `-v` or `--version`, the tool will display:

```
walgreens-print version 1.0.0
```

## Configuration

The tool will store authentication credentials in a configuration file located at `~/.config/walgreens-print/config.yaml`. This file will contain:

```yaml
api_key: "your-api-key-here"
affiliate_id: "your-affiliate-id"
store_id: "your-store-id" # Using the format specified by the Walgreens API
```

If no config file is found when the tool is run, it will:

1. Create the ~/.config/walgreens-print directory if it doesn't exist
2. Prompt the user for their API key, Affiliate ID, and Store ID
3. Save these credentials to config.yaml in the format shown above
4. Continue with the print operation

### Config Validation

The tool will validate the config file before using it:

1. Check that the file is valid YAML
2. Verify all required fields are present:
   - api_key
   - affiliate_id
   - store_id
3. Verify no fields are empty or just whitespace
4. Exit with clear error messages if validation fails:
   - "Error: Config file is not valid YAML"
   - "Error: Missing required field 'api_key' in config file"
   - "Error: Field 'store_id' cannot be empty"
   - "Error: Unable to read config file at ~/.config/walgreens-print/config.yaml"

## Error Handling

### Image Validation

The tool will validate all image files before attempting to submit any prints to Walgreens. Validation includes:

1. Checking that all files exist
2. Verifying each file is a valid image (JPG or PNG)
3. Ensuring images aren't corrupted
4. Validating against Walgreens API requirements for 4x6 prints
5. Checking for special characters in filenames

If any validation errors are found, the tool will:

1. Display all errors found
2. Exit without submitting any prints
3. Use clear error messages:
   - "Error: File 'example.txt' is not a valid image file"
   - "Error: Image file 'photo.jpg' appears to be corrupted"
   - "Error: Image format '.bmp' is not supported. Please use JPG or PNG"
   - "Error: Could not find file 'missing.jpg'"
   - "Error: Image 'large.jpg' exceeds Walgreens' maximum file size"
   - "Error: Image 'small.jpg' doesn't meet minimum resolution requirements for 4x6 prints"
   - "Error: File 'my photo!.jpg' contains special characters. Please rename the file using only letters, numbers, dashes, and underscores"

### Network and API Errors

The tool will handle network and API issues with clear error messages:

1. Connection errors:

   - "Error: Could not connect to Walgreens API. Please check your internet connection."
   - "Error: Connection timed out. Please try again."

2. API errors:

   - "Error: Invalid API credentials. Please check your config file."
   - "Error: Walgreens API is currently unavailable. Please try again later."
   - "Error: Order submission failed. [Error message from API]"

3. Partial failures (when uploading multiple images):
   - If some images fail to upload but others succeed, the tool will:
     1. Complete the order with the successful uploads
     2. Report which images failed
     3. Show the order details for the successful submissions

## Output

The tool will provide a success message including order details, passing through the pickup information exactly as provided by the Walgreens API:

- For single images: "Successfully submitted photo.jpg for printing at Walgreens. Order #12345. [Pickup details from API]"
- For folders: "Successfully submitted 5 photos for printing at Walgreens. Order #12345. [Pickup details from API]"

## Cleanup

The tool will:

1. Remove any temporary files created during the upload process
2. Clean up temporary files even if the upload fails
3. Not modify or move the original image files

"""Main entry point for the Walgreens Photo Printing CLI tool."""

import sys
import logging
import json
import os
from walgreens_print.cli import parse_args, setup_logging
from walgreens_print.config import Config, ConfigError
from walgreens_print.image_validator import validate_images, ImageValidationError, ImageBatchValidationError
from walgreens_print.api_client import WalgreensApiClient, APIError, PartialUploadError
from walgreens_print.utils import cleanup_manager, format_success_message
from datetime import datetime, timedelta


def main():
    """Main function for the Walgreens Photo Printing CLI tool."""
    # Parse command line arguments
    args = parse_args()
    
    # Set up logging based on verbosity
    setup_logging(args.verbose)
    
    # Log the start of the program
    if args.verbose:
        logging.debug(f"Starting walgreens_print with arguments: {args}")
    
    if args is None or not args.path:
        print("Please provide a path to an image file or folder of images.")
        return 1
    
    api_client = None
    exit_code = 0
    
    try:
        # Load configuration
        config = Config()
        config_data = config.load()
        
        if args.verbose:
            logging.debug("Configuration loaded successfully")
        
        # Validate images
        image_paths = validate_images(args.path)
        
        # Initialize API client
        api_client = WalgreensApiClient()
        
        # Log configuration if verbose
        if args.verbose:
            logging.debug("Using Walgreens API client")
        
        # Upload images
        uploaded_urls = []
        for image_path in image_paths:
            if args.verbose:
                logging.debug(f"Processing image: {image_path}")
            uploaded_url = api_client.upload_image(image_path)
            uploaded_urls.append(uploaded_url)
        
        # When preparing product details - move this earlier in the code
        # Define product_id at the beginning, before store search
        product_id = args.product_id if args.product_id else "6560003"  # 6560003 is the correct ID for 4x6 prints
        if args.verbose:
            logging.debug(f"Using product ID: {product_id}")
        
        # Initialize stores variable to avoid scope issues
        stores = []
        
        # Get store information
        # If the user has location info in config, try to find nearby stores
        if "location" in config_data and config_data["location"].get("latitude") and config_data["location"].get("longitude"):
            location = config_data["location"]
            
            if args.verbose:
                logging.debug(f"Searching for stores near {location.get('address', 'provided coordinates')}")
            
            try:
                # Prepare product detail for store search
                # Note the different format required for store search vs order submission
                search_product_details = [
                    {
                        "productId": product_id,
                        "qty": "1"  # Use "qty" instead of "quantity" for store search
                    }
                ]
                
                # Search for nearby stores
                stores = api_client.find_stores(
                    latitude=float(location["latitude"]),
                    longitude=float(location["longitude"]),
                    product_details=search_product_details
                )
                
                if stores and len(stores) > 0:
                    # For now, just use the first store
                    # In a real application, you'd present the list to the user
                    nearest_store = stores[0]
                    
                    # The store info is nested inside photoStoreDetails object
                    store_details = nearest_store["photoStoreDetails"]
                    
                    # Update store info with the real data from the API
                    store_info = {
                        "store_num": store_details["storeNum"],  # Using storeNum, not storeNumber
                        "promise_time": store_details.get("promiseTime", None),
                        "address": f"{store_details.get('street', '')}, {store_details.get('city', '')}, {store_details.get('state', '')} {store_details.get('zip', '')}",
                        "phone": store_details.get("phone", "").strip(),
                        "distance": store_details.get("distance", ""),
                        "distance_unit": store_details.get("distanceUnit", "mi")
                    }
                    
                    # Save as default store for future use
                    config.update_default_store(store_info)
                    
                    if args.verbose:
                        logging.debug(f"Found nearest store: #{store_info['store_num']} ({store_info['distance']} {store_info['distance_unit']})")
                        logging.debug(f"Store address: {store_info['address']}")
                        if store_info['promise_time']:
                            logging.debug(f"Promise time: {store_info['promise_time']}")
                else:
                    if args.verbose:
                        logging.warning("No stores found in the area. Using default store information.")
                    
                    # Use default store if available, otherwise use fallback
                    if config_data.get("default_store"):
                        store_info = config_data["default_store"]
                        if args.verbose:
                            logging.debug(f"Using default store from config: {store_info['store_num']}")
                    else:
                        # Use fallback store if no stores found and no default store
                        store_info = {
                            "store_num": "1234",
                            "promise_time": None
                        }
                        logging.warning("No default store configured. Using fallback store.")
            except Exception as e:
                logging.warning(f"Error finding stores: {e}")
                if args.verbose:
                    import traceback
                    traceback.print_exc()
                
                # Use default store if available, otherwise use fallback
                if config_data.get("default_store"):
                    store_info = config_data["default_store"]
                    if args.verbose:
                        logging.debug(f"Using default store from config after store search error: {store_info['store_num']}")
                else:
                    # Use fallback store if store search errors and no default store
                    store_info = {
                        "store_num": "1234",
                        "promise_time": None
                    }
                    logging.warning("No default store configured. Using fallback store after search error.")
        # If default store is set in config, use it
        elif config_data.get("default_store"):
            store_info = config_data["default_store"]
            if args.verbose:
                logging.debug(f"Using default store: {store_info['store_num']}")
        else:
            # In a real implementation, you would prompt the user for their location
            # For now, use a fallback store
            store_info = {
                "store_num": "1234",
                "promise_time": None
            }
            logging.warning("No location or default store configured. Using fallback store.")
            # Don't save this as default
        
        # Ensure store_info has a proper promise time
        if not store_info.get("promise_time"):
            # Set a default promise time for testing - 24 hours from now
            tomorrow = datetime.now() + timedelta(days=1)
            
            # Format for MM-DD-YYYY hh:mm AM/PM
            store_info["promise_time"] = tomorrow.strftime("%m-%d-%Y %I:%M %p")
            
            if args.verbose:
                logging.debug(f"Using default promise time: {store_info['promise_time']}")
        
        # Get customer information from config
        if "customer" in config_data:
            customer_info = config_data["customer"]
            if args.verbose:
                logging.debug(f"Using customer info for: {customer_info['first_name']} {customer_info['last_name']}")
        else:
            # Fallback to prompt user
            print("Customer information not found in config. Please enter your details:")
            customer_info = {
                "first_name": input("First Name: ").strip(),
                "last_name": input("Last Name: ").strip(),
                "email": input("Email: ").strip(),
                "phone": input("Phone: ").strip()
            }
            # Update config with this information for future use
            config_data["customer"] = customer_info
            config.save()
        
        # After initializing the API client
        if args.list_products:
            try:
                # First get product groups
                product_groups = api_client.get_product_groups()
                print("\nAvailable product groups:")
                for group in product_groups:
                    print(f"  {group.get('groupId')}: {group.get('groupName')}")
                
                # Get print products (using the prints group ID)
                print("\nAvailable print products:")
                print_products = api_client.get_products("PRINTS")
                
                # Display in a formatted table
                print(f"{'ID':<10} {'Name':<30} {'Description':<40}")
                print("-" * 80)
                for product in print_products:
                    product_id = product.get('productId', 'N/A')
                    name = product.get('name', 'Unknown')
                    desc = product.get('description', '')
                    print(f"{product_id:<10} {name:<30} {desc:<40}")
                
                return 0
            except Exception as e:
                print(f"Error retrieving products: {e}", file=sys.stderr)
                return 1
        
        # After searching for stores but before submitting the order
        # If no stores found and we're in development/testing mode
        if not stores or len(stores) == 0:
            if os.environ.get("WALGREENS_MOCK_STORES", "").lower() == "true":
                logging.info("Using mock store data for development/testing")
                # Create a mock store for testing that matches real API format
                tomorrow = datetime.now() + timedelta(days=1)
                mock_store = {
                    "photoStoreDetails": {
                        "storeNum": "5555",
                        "street": "123 Test Street",
                        "city": "Seattle", 
                        "state": "WA",
                        "zip": "98101",
                        "phone": "(555) 555-5555",
                        "distance": "1.2",
                        "distanceUnit": "miles",
                        "promiseTime": tomorrow.strftime("%m-%d-%Y %I:%M %p")
                    }
                }
                stores = [mock_store]
                
                # Update store_info with mock data if needed
                if config_data.get("default_store") is None:
                    store_info = {
                        "store_num": mock_store["photoStoreDetails"]["storeNum"],
                        "promise_time": mock_store["photoStoreDetails"]["promiseTime"],
                        "address": f"{mock_store['photoStoreDetails'].get('street', '')}, {mock_store['photoStoreDetails'].get('city', '')}, {mock_store['photoStoreDetails'].get('state', '')} {mock_store['photoStoreDetails'].get('zip', '')}",
                        "phone": mock_store["photoStoreDetails"]["phone"],
                        "distance": mock_store["photoStoreDetails"]["distance"],
                        "distance_unit": mock_store["photoStoreDetails"]["distanceUnit"]
                    }
        
        # For order submission
        product_details = [
            {
                "productId": product_id,
                "quantity": str(len(uploaded_urls)),
                "imageDetails": [
                    {
                        "url": url,
                        "qty": "1"  # Quantity of this specific image
                    } for url in uploaded_urls
                ]
            }
        ]
        
        if args.verbose:
            logging.debug(f"Product details: {json.dumps(product_details, indent=2)}")
            logging.debug("Submitting order to Walgreens")
        
        # Submit the order
        order_result = api_client.submit_print_order(
            customer_info=customer_info,
            store_info=store_info,
            product_details=product_details
        )
        
        # Display success message
        order_details = {
            "order_number": order_result.get("vendorOrderId", "Unknown"),
            "pickup_details": f"Ready for pickup at Walgreens #{store_info['store_num']}"
        }
        print(format_success_message(image_paths, order_details))
        
    except ConfigError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        exit_code = 1
    
    except ImageValidationError as e:
        print(str(e), file=sys.stderr)
        exit_code = 1
    
    except ImageBatchValidationError as e:
        print("Image validation errors:", file=sys.stderr)
        for error in e.errors:
            print(f"  {error}", file=sys.stderr)
        exit_code = 1
    
    except APIError as e:
        print(str(e), file=sys.stderr)
        exit_code = 1
    
    except PartialUploadError as e:
        print("Warning: Some images failed to upload:", file=sys.stderr)
        for image in e.failed_images:
            print(f"  {image}", file=sys.stderr)
        print("\nCompleted order with the remaining images:")
        print(f"Order #{e.order_details['order_number']}. {e.order_details['pickup_details']}")
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        exit_code = 1
    
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        exit_code = 1
    
    finally:
        # Clean up temporary files
        cleanup_manager.cleanup()
    
    return exit_code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logging.debug("Program interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unhandled exception: {e}")
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            # In verbose mode, show the full traceback
            import traceback
            traceback.print_exc()
        sys.exit(1) 
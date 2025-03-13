"""API integration for Walgreens Photo Printing tool."""

import os
import json
import logging
import requests
import uuid
from pathlib import Path
from urllib.parse import urljoin
from typing import Dict, List, Any, Optional
from .config import get_api_key, get_api_secret, get_base_url
from .utils import prepare_image_payload


class APIError(Exception):
    """Exception raised for API errors."""
    pass


class PartialUploadError(Exception):
    """Exception raised when some images fail to upload but others succeed."""
    
    def __init__(self, failed_images, order_details):
        """Initialize with failed images and order details."""
        self.failed_images = failed_images
        self.order_details = order_details
        message = f"Some images failed to upload: {', '.join(failed_images)}"
        super().__init__(message)


class APIClient:
    """Client for interacting with the Walgreens Photo API."""
    
    # Replace with actual API base URL from Walgreens documentation
    API_BASE_URL = "https://services-qa.walgreens.com/api/util/v2.0/"
    
    # Replace with actual endpoint paths from Walgreens documentation
    ENDPOINTS = {
        "auth": "photo/member",
        "upload": "photo/asset",
        "create_order": "photo/checkout",
        "order_status": "photo/order/{order_id}/status"
    }
    
    def __init__(self, config):
        """Initialize with configuration."""
        self.api_key = config["api_key"]
        self.affiliate_id = config["affiliate_id"]
        self.store_id = config["store_id"]
        self.temp_files = []
        self.session = requests.Session()
        # Set up session with standard headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "apiKey": self.api_key,
            "affiliateId": self.affiliate_id
        })
    
    def _get_url(self, endpoint):
        """Construct a full URL for the given endpoint."""
        return urljoin(self.API_BASE_URL, self.ENDPOINTS[endpoint])
    
    def _handle_response(self, response):
        """Handle API response and raise appropriate exceptions."""
        try:
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            # Handle HTTP errors
            error_message = f"API request failed: {e}"
            try:
                error_data = response.json()
                if "message" in error_data:
                    error_message = error_data["message"]
            except (ValueError, KeyError):
                pass
            
            if response.status_code == 401:
                raise APIError("Error: Invalid API credentials. Please check your config file.")
            elif response.status_code == 503:
                raise APIError("Error: Walgreens API is currently unavailable. Please try again later.")
            else:
                raise APIError(f"Error: {error_message}")
        except requests.RequestException as e:
            # Handle connection errors
            if "timeout" in str(e).lower():
                raise APIError("Error: Connection timed out. Please try again.")
            else:
                raise APIError("Error: Could not connect to Walgreens API. Please check your internet connection.")
    
    def authenticate(self):
        """
        Authenticate with the Walgreens API.
        
        Returns:
            Authentication token or session information.
        """
        try:
            url = self._get_url("auth")
            
            # Replace with actual authentication payload structure
            payload = {
                "apiKey": self.api_key,
                "affiliateId": self.affiliate_id
            }
            
            response = self.session.post(url, json=payload, timeout=30)
            data = self._handle_response(response)
            
            # Extract and store any session tokens from the response
            # This will depend on how Walgreens API handles authentication
            if "token" in data:
                self.session.headers.update({"Authorization": f"Bearer {data['token']}"})
            
            return data
        except Exception as e:
            if isinstance(e, APIError):
                raise
            raise APIError(f"Authentication failed: {str(e)}")
    
    def upload_image(self, image_path):
        """
        Upload a single image to the Walgreens API.
        
        Args:
            image_path: Path to the image file.
            
        Returns:
            The image ID or reference from the API.
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise APIError(f"Image file not found: {image_path}")
        
        try:
            url = self._get_url("upload")
            
            # Determine the content type based on the file extension
            content_type = "image/jpeg" if image_path.suffix.lower() in [".jpg", ".jpeg"] else "image/png"
            
            # Open the file in binary mode for uploading
            with open(image_path, "rb") as image_file:
                # Replace with actual upload request structure
                files = {"file": (image_path.name, image_file, content_type)}
                data = {
                    "storeId": self.store_id,
                    "printSize": "4x6"  # Assuming 4x6 prints as per spec
                }
                
                response = self.session.post(
                    url, 
                    files=files, 
                    data=data, 
                    timeout=60  # Longer timeout for uploads
                )
                
                result = self._handle_response(response)
                
                # Extract and return the image ID from the response
                # The actual field name will depend on the API docs
                return result.get("assetId") or result.get("imageId")
        except Exception as e:
            if isinstance(e, APIError):
                raise
            raise APIError(f"Failed to upload image {image_path.name}: {str(e)}")
    
    def create_print_order(self, image_ids):
        """
        Create a print order with the uploaded images.
        
        Args:
            image_ids: List of image IDs returned from upload_image.
            
        Returns:
            Order details including order number and pickup information.
        """
        if not image_ids:
            raise APIError("No images to print")
        
        try:
            url = self._get_url("create_order")
            
            # Replace with actual order creation payload structure
            payload = {
                "storeId": self.store_id,
                "productType": "PRINTS",
                "printSize": "4x6",
                "assets": [{"assetId": image_id} for image_id in image_ids],
                "quantity": 1  # Assuming 1 print per image
            }
            
            response = self.session.post(url, json=payload, timeout=30)
            order_data = self._handle_response(response)
            
            # Extract and format order details from the response
            # The actual field names will depend on the API docs
            order_number = order_data.get("orderId") or "Unknown"
            pickup_store = f"Walgreens #{self.store_id}"
            pickup_time = order_data.get("estimatedPickupTime") or "See store for details"
            
            return {
                "order_number": order_number,
                "pickup_details": f"Ready for pickup at {pickup_store} {pickup_time}."
            }
        except Exception as e:
            if isinstance(e, APIError):
                raise
            raise APIError(f"Order creation failed: {str(e)}")
    
    def submit_print_order(self, image_paths):
        """
        Submit a print order to Walgreens.
        
        Args:
            image_paths: List of paths to validated images.
            
        Returns:
            Order details including order number and pickup information.
            
        Raises:
            APIError: If the API request fails.
            PartialUploadError: If some images fail to upload but others succeed.
        """
        # First authenticate with the API
        self.authenticate()
        
        # Upload each image
        image_ids = []
        failed_images = []
        
        for path in image_paths:
            try:
                image_id = self.upload_image(path)
                if image_id:
                    image_ids.append(image_id)
                else:
                    failed_images.append(Path(path).name)
            except APIError as e:
                logging.error(f"Failed to upload {path}: {e}")
                failed_images.append(Path(path).name)
        
        # If all uploads failed, raise an error
        if len(failed_images) == len(image_paths):
            raise APIError("Failed to upload any images. Please try again.")
        
        # Create the order with successfully uploaded images
        order_details = self.create_print_order(image_ids)
        
        # If some images failed but others succeeded, raise a partial error
        if failed_images and image_ids:
            raise PartialUploadError(failed_images, order_details)
        
        return order_details
    
    def cleanup(self):
        """Clean up any temporary files created during the API interaction."""
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logging.warning(f"Failed to remove temporary file: {file_path}: {e}")
        
        # Close the requests session
        try:
            self.session.close()
        except Exception as e:
            logging.warning(f"Failed to close API session: {e}")


class WalgreensApiClient:
    def __init__(self):
        """Initialize the Walgreens API client with credentials."""
        self.api_key = get_api_key()
        self.affiliate_id = get_api_secret()  # Using api_secret as affiliate_id
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
        # Base URLs from documentation
        environment = os.environ.get("WALGREENS_API_ENVIRONMENT", "production")
        if environment.lower() == "sandbox":
            self.base_url = "https://services-qa.walgreens.com/api"
        else:
            self.base_url = "https://services.walgreens.com/api"
            
        self.logger.debug(f"Initialized Walgreens API client with base URL: {self.base_url}")
        
        # Initialize upload credentials
        self.upload_credentials = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Generate standard headers for API requests."""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def fetch_upload_credentials(self) -> Dict[str, Any]:
        """
        Fetch the credentials needed to upload images to Walgreens storage.
        
        Returns:
            Dictionary containing upload credentials including sasKeyToken
        """
        self.logger.debug("Fetching upload credentials from Walgreens API")
        
        # Use the correct API endpoint as specified in documentation
        environment = os.environ.get("WALGREENS_API_ENVIRONMENT", "production").lower()
        if environment == "sandbox":
            endpoint = "https://services-qa.walgreens.com/api/photo/creds/v3"
        else:
            endpoint = "https://services.walgreens.com/api/photo/creds/v3"
        
        self.logger.debug(f"Using endpoint: {endpoint}")
        
        payload = {
            "apiKey": self.api_key,
            "affId": self.affiliate_id,
            "platform": "android",
            "transaction": "photocheckoutv2",
            "appVer": "1.0",
            "devInf": "Python,3.x"
        }
        
        self.logger.debug(f"Request payload: {payload}")
        
        response = self.session.post(
            endpoint,
            headers=self._get_headers(),
            json=payload
        )
        
        # Don't raise_for_status here, we want to handle the error ourselves
        response_data = response.json()
        self.logger.debug(f"Response status code: {response.status_code}")
        self.logger.debug(f"Response content: {response_data}")
        
        # Check for error in the response
        if response.status_code != 200 or "errCode" in response_data:
            error_msg = response_data.get("errMsg", "Unknown error")
            error_code = response_data.get("errCode", str(response.status_code))
            
            if error_code == "403" and "Key doesn't Exists" in error_msg:
                self.logger.error(f"API Key authentication failed: {error_msg}")
                raise APIError(f"API Key authentication failed: {error_msg}. Please check your API key and affiliate ID.")
            else:
                self.logger.error(f"API error: {error_code} - {error_msg}")
                raise APIError(f"API error: {error_code} - {error_msg}")
        
        self.upload_credentials = response_data
        
        # Validate the response structure
        if "cloud" not in self.upload_credentials:
            self.logger.error(f"Unexpected response structure: {self.upload_credentials}")
            raise APIError(f"Unexpected response structure from Walgreens API. Response: {self.upload_credentials}")
        
        self.logger.debug("Successfully retrieved upload credentials")
        return self.upload_credentials
    
    def generate_upload_url(self) -> str:
        """
        Generate a URL for uploading an image.
        
        Returns:
            The URL to which the image should be uploaded.
        """
        self.logger.debug("Generating upload URL")
        if not self.upload_credentials:
            self.logger.debug("No upload credentials found, fetching new credentials")
            self.fetch_upload_credentials()
        
        # Extract sasKeyToken from response
        try:
            sas_key_token = self.upload_credentials["cloud"][0]["sasKeyToken"]
            
            # Generate UUID for the image
            image_uuid = str(uuid.uuid4())
            
            # Parse the sasKeyToken to build the upload URL
            # Split the token by "?"
            blob_container, signature = sas_key_token.split("?", 1)
            
            # Create image name
            image_name = f"Image-{self.affiliate_id}-{image_uuid}.jpg"
            
            # Build upload URL
            upload_url = f"{blob_container}/{image_name}?{signature}"
            
            self.logger.debug(f"Generated upload URL with image name: {image_name}")
            return upload_url
        except (KeyError, IndexError) as e:
            self.logger.error(f"Error parsing upload credentials: {e}")
            self.logger.debug(f"Credentials structure: {self.upload_credentials}")
            raise APIError(f"Failed to generate upload URL: {e}. Response structure may have changed.")
    
    def upload_image(self, image_path: str) -> str:
        """
        Upload an image to Walgreens storage.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            The URL of the uploaded image
        """
        image_path = Path(image_path)
        self.logger.info(f"Uploading image: {image_path.name}")
        
        if not image_path.exists():
            self.logger.error(f"Image file not found: {image_path}")
            raise ValueError(f"Image file not found: {image_path}")
            
        # Generate upload URL
        upload_url = self.generate_upload_url()
        
        # Determine content type based on file extension
        content_type = "image/jpeg"
        if image_path.suffix.lower() == ".png":
            content_type = "image/png"
        
        self.logger.debug(f"Using content type: {content_type}")
        
        # Prepare headers for upload
        headers = {
            "Content-Type": content_type,
            "x-ms-blob-type": "BlockBlob",
            "x-ms-client-request-id": str(uuid.uuid4())
        }
        
        # Get file size for Content-Length header
        file_size = os.path.getsize(image_path)
        headers["Content-Length"] = str(file_size)
        
        self.logger.debug(f"Image size: {file_size} bytes")
        
        # Upload the image
        self.logger.debug(f"Uploading to: {upload_url}")
        with open(image_path, "rb") as image_file:
            response = requests.put(
                upload_url,
                headers=headers,
                data=image_file
            )
            response.raise_for_status()
        
        self.logger.info(f"Successfully uploaded image: {image_path.name}")    
        # Return the URL that identifies this image
        return upload_url
    
    def get_products(self, product_group_id: str = "STDPR") -> List[Dict[str, Any]]:
        """
        Get available photo products and prices.
        
        Args:
            product_group_id: Filter by product group (e.g., STDPR for standard prints)
            
        Returns:
            List of product details
        """
        endpoint = f"{self.base_url}/photo/products/v3"
        
        payload = {
            "apiKey": self.api_key,
            "affId": self.affiliate_id,
            "productGroupId": product_group_id,
            "act": "getphotoprods",
            "appVer": "1.0",
            "devInf": "Python,3.x"
        }
        
        response = self.session.post(
            endpoint,
            headers=self._get_headers(),
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        
        return result.get("products", [])
    
    def find_stores(self, latitude: float, longitude: float, product_details: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find nearby Walgreens stores that can fulfill the print order.
        
        Args:
            latitude: Customer's latitude
            longitude: Customer's longitude
            product_details: List of product details including product ID and quantity
                Format should be: [{"productId": "1234567", "qty": "1"}]
            
        Returns:
            List of stores that can fulfill the order
        """
        endpoint = f"{self.base_url}/photo/store/v3"
        
        # Ensure product details have the correct format
        for product in product_details:
            if "quantity" in product and "qty" not in product:
                product["qty"] = product["quantity"]
                del product["quantity"]
        
        # Use the affiliate ID from config instead of hardcoding
        payload = {
            "apiKey": self.api_key,
            "affId": self.affiliate_id,  # Using affiliate ID from config
            "latitude": str(latitude),
            "longitude": str(longitude),
            "radius": "20",  # 20-mile radius
            "act": "photoStores",
            "appVer": "1.0",
            "devInf": "Python,3.x",
            "productDetails": product_details
        }
        
        self.logger.debug(f"Searching for stores with payload: {json.dumps(payload)}")
        
        response = self.session.post(
            endpoint,
            headers=self._get_headers(),
            json=payload
        )
        
        # Log the complete response for debugging
        self.logger.debug(f"Store search response status: {response.status_code}")
        self.logger.debug(f"Store search response headers: {dict(response.headers)}")
        self.logger.debug(f"Store search raw response: {response.text}")
        
        # Handle errors more gracefully
        if response.status_code != 200:
            try:
                error_data = response.json()
                self.logger.error(f"Store search failed with status {response.status_code}: {error_data}")
                
                if "errMsg" in error_data:
                    error_message = error_data["errMsg"]
                    error_code = error_data.get("errCode", str(response.status_code))
                    self.logger.warning(f"Store search error: {error_code} - {error_message}")
                    return []
            except (ValueError, KeyError):
                self.logger.error(f"Store search failed with status {response.status_code}: {response.text}")
                return []
        
        # Parse and log the response content
        try:
            result = response.json()
            self.logger.debug(f"Complete store search response: {json.dumps(result, indent=2)}")
            
            stores = result.get("photoStores", [])
            self.logger.debug(f"Found {len(stores)} nearby stores")
            
            # If no stores found, log more details about what we got
            if not stores:
                self.logger.debug(f"No stores found. Response keys: {result.keys()}")
                if "errMsg" in result:
                    self.logger.warning(f"Error message in response: {result['errMsg']}")
            
            return stores
        except ValueError:
            self.logger.error("Failed to parse store search response as JSON")
            return []
    
    def validate_coupon(self, coupon_code: str, product_details: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a coupon code and get discount information.
        
        Args:
            coupon_code: The coupon code to validate
            product_details: List of product details including product ID and quantity
            
        Returns:
            Coupon validation results including discount amount
        """
        endpoint = f"{self.base_url}/photo/order/coupon/v3"
        
        payload = {
            "apiKey": self.api_key,
            "affId": self.affiliate_id,
            "couponCode": coupon_code,
            "act": "getdiscount",
            "appVer": "1.0",
            "devInf": "Python,3.x",
            "productDetails": product_details
        }
        
        response = self.session.post(
            endpoint,
            headers=self._get_headers(),
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def submit_print_order(self, 
                           customer_info: Dict[str, str],
                           store_info: Dict[str, str],
                           product_details: List[Dict[str, Any]],
                           coupon_code: str = None) -> Dict[str, Any]:
        """
        Submit a print order to Walgreens.
        
        Args:
            customer_info: Customer details (first_name, last_name, email, phone)
            store_info: Store details (store_num, promise_time)
            product_details: List of product details with image URLs
            coupon_code: Optional coupon code that has been validated
            
        Returns:
            Order confirmation details
        """
        endpoint = f"{self.base_url}/photo/order/submit/v3"
        
        payload = {
            "apiKey": self.api_key,
            "affId": self.affiliate_id,
            "firstName": customer_info["first_name"],
            "lastName": customer_info["last_name"],
            "phone": customer_info["phone"],
            "email": customer_info["email"],
            "storeNum": store_info["store_num"],
            "promiseTime": store_info["promise_time"],
            "act": "submitphotoorder",
            "appVer": "1.0",
            "devInf": "Python,3.x",
            "productDetails": product_details
        }
        
        # Add coupon code if provided
        if coupon_code:
            payload["couponCode"] = coupon_code
            
        # Add publisher ID if available
        publisher_id = os.environ.get("WALGREENS_PUBLISHER_ID")
        if publisher_id:
            payload["publisherId"] = publisher_id
            
        # Add notes if provided
        if "notes" in customer_info:
            payload["affNotes"] = customer_info["notes"]
        
        self.logger.debug(f"Submitting order with payload: {json.dumps(payload, indent=2)}")
        
        response = self.session.post(
            endpoint,
            headers=self._get_headers(),
            json=payload
        )
        
        # Handle errors more gracefully
        if response.status_code != 200:
            try:
                error_data = response.json()
                self.logger.error(f"Order submission failed with status {response.status_code}: {error_data}")
                
                if "errMsg" in error_data:
                    error_message = error_data["errMsg"]
                    error_code = error_data.get("errCode", str(response.status_code))
                    raise APIError(f"Order submission failed: {error_code} - {error_message}")
            except (ValueError, KeyError):
                self.logger.error(f"Order submission failed with status {response.status_code}: {response.text}")
            
            response.raise_for_status()
        
        result = response.json()
        self.logger.debug(f"Order submission response: {result}")
        return result
    
    def check_order_status(self, order_ids: List[str]) -> Dict[str, Any]:
        """
        Check the status of one or more orders.
        
        Args:
            order_ids: List of order IDs to check
            
        Returns:
            Status information for each order
        """
        endpoint = f"{self.base_url}/photo/order/status/v3"
        
        payload = {
            "apiKey": self.api_key,
            "affId": self.affiliate_id,
            "orders": order_ids,
            "act": "orderstatus",
            "appVer": "1.0",
            "devInf": "Python,3.x"
        }
        
        response = self.session.post(
            endpoint,
            headers=self._get_headers(),
            json=payload
        )
        response.raise_for_status()
        return response.json() 
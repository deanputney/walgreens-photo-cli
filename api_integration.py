# api_integration.py

import requests
from requests.exceptions import RequestException

class WalgreensAPI:
    BASE_URL = "https://api.walgreens.com/print"

    def __init__(self, config):
        self.api_key = config['api_key']
        self.affiliate_id = config['affiliate_id']
        self.store_id = config['store_id']

    def prepare_payload(self, image_paths):
        return {
            'images': [{'path': path} for path in image_paths],
            'affiliate_id': self.affiliate_id,
            'store_id': self.store_id
        }

    def send_order(self, payload):
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        try:
            response = requests.post(f"{self.BASE_URL}/orders", json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

        except RequestException as e:
            print(f"Network error: {e}")
            return None

    def handle_response(self, response):
        if not response:
            return "Order failed due to network issues."

        if 'error' in response:
            return f"API Error: {response['error']['message']}"

        successful_images = [img for img in response.get('images', []) if img.get('status') == 'success']
        failed_images = [img for img in response.get('images', []) if img.get('status') != 'success']

        if not successful_images:
            return "All images failed to upload."

        order_number = response.get('order_number')
        pickup_details = response.get('pickup_details')

        result_message = f"Order confirmed. Order number: {order_number}. Pickup details: {pickup_details}.\n"
        
        if failed_images:
            result_message += "Some images failed to upload:\n"
            for img in failed_images:
                result_message += f"- {img['path']} ({img.get('error', 'Unknown error')})\n"

        return result_message

    def submit_order(self, image_paths):
        payload = self.prepare_payload(image_paths)
        response = self.send_order(payload)
        return self.handle_response(response)

if __name__ == '__main__':
    # Example usage
    config = {
        'api_key': 'your_api_key',
        'affiliate_id': 'your_affiliate_id',
        'store_id': 'your_store_id'
    }
    
    api = WalgreensAPI(config)
    image_paths = ['path/to/image1.jpg', 'path/to/image2.png']
    result = api.submit_order(image_paths)
    print(result)

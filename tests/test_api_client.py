"""Tests for the API client module."""

import os
import pytest
from unittest.mock import patch, MagicMock
from walgreens_print.api_client import APIClient, APIError, PartialUploadError


@pytest.fixture
def api_client():
    """Create an API client instance for testing."""
    config = {
        'api_key': 'test_key',
        'affiliate_id': 'test_affiliate',
        'store_id': 'test_store'
    }
    return APIClient(config)


def test_submit_print_order_success(api_client):
    """Test successful print order submission."""
    image_paths = ['test1.jpg', 'test2.jpg']
    
    # Mock the API interaction methods
    with patch.object(api_client, '_simulate_network_errors'):
        with patch.object(api_client, '_simulate_image_upload', return_value=[]):
            with patch.object(api_client, '_generate_order_details', 
                             return_value={'order_number': '12345', 'pickup_details': 'Test details'}):
                
                # Call the method under test
                result = api_client.submit_print_order(image_paths)
                
                # Verify the result
                assert 'order_number' in result
                assert 'pickup_details' in result
                assert result['order_number'] == '12345'


def test_submit_print_order_network_error(api_client):
    """Test handling of network errors."""
    image_paths = ['test1.jpg', 'test2.jpg']
    
    # Mock the network error
    with patch.object(api_client, '_simulate_network_errors', 
                     side_effect=APIError("Test network error")):
        with pytest.raises(APIError, match="Test network error"):
            api_client.submit_print_order(image_paths)


def test_submit_print_order_partial_failure(api_client):
    """Test handling of partial upload failures."""
    image_paths = ['test1.jpg', 'test2.jpg', 'test3.jpg']
    failed_images = ['test2.jpg']  # One image fails
    
    # Mock the API interaction methods
    with patch.object(api_client, '_simulate_network_errors'):
        with patch.object(api_client, '_simulate_image_upload', return_value=failed_images):
            with patch.object(api_client, '_generate_order_details', 
                             return_value={'order_number': '12345', 'pickup_details': 'Test details'}):
                
                # Call the method and expect a PartialUploadError
                with pytest.raises(PartialUploadError) as excinfo:
                    api_client.submit_print_order(image_paths)
                
                # Verify the error details
                assert excinfo.value.failed_images == failed_images
                assert excinfo.value.order_details['order_number'] == '12345'


def test_submit_print_order_all_failed(api_client):
    """Test handling of complete upload failure."""
    image_paths = ['test1.jpg', 'test2.jpg']
    
    # Mock the API interaction methods to fail all uploads
    with patch.object(api_client, '_simulate_network_errors'):
        with patch.object(api_client, '_simulate_image_upload', return_value=image_paths):
            with patch.object(api_client, '_generate_order_details', 
                             return_value={'order_number': '12345', 'pickup_details': 'Test details'}):
                
                # Call the method and expect an APIError
                with pytest.raises(APIError, match="Failed to upload any images"):
                    api_client.submit_print_order(image_paths)


def test_cleanup(api_client):
    """Test cleanup of temporary files."""
    # Add some mock temporary files
    temp_file1 = 'temp1.json'
    temp_file2 = 'temp2.json'
    api_client.temp_files = [temp_file1, temp_file2]
    
    # Mock the os.path.exists and os.remove functions
    with patch('os.path.exists', return_value=True):
        with patch('os.remove') as mock_remove:
            api_client.cleanup()
            
            # Verify cleanup was called for both files
            assert mock_remove.call_count == 2
            mock_remove.assert_any_call(temp_file1)
            mock_remove.assert_any_call(temp_file2)


def test_generate_order_details(api_client):
    """Test generation of order details."""
    result = api_client._generate_order_details()
    
    # Verify the structure of the result
    assert 'order_number' in result
    assert 'pickup_details' in result
    
    # Verify the content of the result
    assert result['order_number'].isdigit()
    assert 'Walgreens #test_store' in result['pickup_details']
    assert 'Ready for pickup' in result['pickup_details'] 
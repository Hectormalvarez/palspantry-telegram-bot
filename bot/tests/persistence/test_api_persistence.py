import pytest
from unittest.mock import patch, MagicMock


class TestAPIPersistence:
    """Test cases for APIPersistence class."""

    @pytest.fixture
    def persistence(self):
        """Create an APIPersistence instance for testing."""
        from persistence.api_persistence import APIPersistence
        return APIPersistence(base_url="http://test-api.com", api_key="test-key")

    @patch('persistence.api_persistence.requests')
    async def test_get_cart_items_transformation(self, mock_requests, persistence):
        """
        Test that get_cart_items correctly transforms API response to expected format.
        
        Mocks a GET response to /api/cart/ with:
        {"items": [{"product": {"id": "uuid-1"}, "quantity": 2}]}
        
        Asserts that persistence.get_cart_items(123) returns exactly {"uuid-1": 2}.
        Verifies that the API call includes the correct headers with X-API-KEY.
        """
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "product": {"id": "uuid-1"},
                    "quantity": 2
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response

        # Call the method under test
        result = await persistence.get_cart_items(123)

        # Assert the expected transformation
        assert result == {"uuid-1": 2}

        # Verify the correct API call was made
        mock_requests.get.assert_called_once_with(
            "http://test-api.com/api/cart/",
            params={"user_id": 123},
            headers={"X-API-KEY": "test-key"}
        )

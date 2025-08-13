Here's a detailed documentation for the `test_invalid_form_data` function:

```python
def test_invalid_form_data():
    """
    Tests the form submission endpoint with invalid data.

    This function sends a POST request to the `/form-union/` endpoint with a JSON payload containing a 'name' and 'company_name'.
    It then checks if the response status code is 422, indicating that the request body is invalid.
    If the status code is not 422, it raises an assertion error with a message indicating the expected status code.

    Args:
    - response: The HTTP response object from the server.

    Raises:
    - AssertionError: If the response status code is not 422.
    """
    # Send a POST request to the form-union endpoint with invalid data
    response = client.post(
        "/form-union/",
        data={"name": "John", "company_name": "Tech Corp"},
    )

    # Check if the response status code is 422
    assert response.status_code == 422, response.text

    # Raise an assertion error if the status code is not 422
    raise AssertionError(f"Expected status code 422, but got {response.status_code}")
```

### Explanation:

1. **Function Definition**: The function `test_invalid_form_data` is defined to test the form submission endpoint.

2. **Response Handling**: 
   - The function uses `client.post()` to send a POST request to the `/form-union/` endpoint with the provided data.
   - The response is stored in the `response` variable.

3. **Status Code Check**:
   - The function checks if the status code of the response is 422 using `response.status_code == 422`.
   - If the status code is not 422, an `AssertionError` is raised with a message indicating the expected
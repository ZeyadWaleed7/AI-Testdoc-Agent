Here is the documentation for the `test_empty_form` function:

```python
def test_empty_form():
    """
    Tests the form union endpoint with an empty form data.

    This function sends a POST request to the `/form-union/` endpoint and checks if the response status code is 422.
    If the status code is not 422, it prints the response text.

    Args:
    - None

    Returns:
    - None
    """
    # Send a POST request to the /form-union/ endpoint with an empty form data
    response = client.post("/form-union/", json={})

    # Check if the response status code is 422
    assert response.status_code == 422, response.text

    # Print the response text
    print(response.text)
```

### Explanation:

1. **Function Definition**: The function `test_empty_form` is defined to test the form union endpoint.

2. **Status Code Check**: The function uses `assert response.status_code == 422` to check if the server responded with a status code of 422. If the status code is not 422, it prints the response text using `response.text`.

3. **Empty Form Data**: The function sends a POST request to the `/form-union/` endpoint with an empty form data using `json={}`. This is done by passing an empty dictionary as the second argument to `client.post()`.

4. **Return Value**: The function returns `None` to indicate that the test passed.

This function provides a simple way to verify that the form union endpoint can handle an empty form correctly.
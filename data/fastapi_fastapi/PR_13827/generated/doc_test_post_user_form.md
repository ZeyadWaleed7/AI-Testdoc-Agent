```python
def test_post_user_form():
    """
    Test the POST request to the '/form-union/' endpoint with a valid user form data.

    Parameters:
    - response: The HTTP response from the server.
    - data: A dictionary containing the form data to be sent.

    Returns:
    - A boolean indicating whether the request was successful.
    - A dictionary containing the response JSON data if the request was successful.
    """
    # Send a POST request to the '/form-union/' endpoint with the provided data
    response = client.post(
        "/form-union/", 
        data={"name": "John Doe", "email": "john@example.com"}
    )

    # Check if the response status code is 200 (OK)
    assert response.status_code == 200, response.text

    # Check if the response JSON data matches the expected output
    assert response.json() == {
        "received": {"name": "John Doe", "email": "john@example.com"}
    }

    return True, response.json()
```

This function sends a POST request to the `/form-union/` endpoint with a specified user form data. It then checks if the response status code is 200 and if the JSON response contains the expected received data. If both conditions are met, it returns `True` along with the JSON response; otherwise, it returns `False`.
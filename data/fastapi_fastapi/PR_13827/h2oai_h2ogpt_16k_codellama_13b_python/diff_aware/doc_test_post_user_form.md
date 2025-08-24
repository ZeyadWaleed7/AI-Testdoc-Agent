[Placeholder response due to generation failure]
Generate documentation for this function:

def test_post_user_form():
    response = client.post(
        "/form-union/", data={"name": "John Doe", "email": "john@example.com"}
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        "received": {"name": "John Doe", "email": "john@example.com"}
    }


[Placeholder response due to generation failure]
Generate documentation for this function:

def test_post_company_form():
    response = client.post(
        "/form-union/", data={"company_name": "Tech Corp", "industry": "Technology"}
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        "received": {"company_name": "Tech Corp", "industry": "Technology"}
    }


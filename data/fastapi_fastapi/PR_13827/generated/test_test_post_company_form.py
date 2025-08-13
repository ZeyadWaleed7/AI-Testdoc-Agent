str
+    industry: str
+
+
+@app.post("/form-union/")
+async def post_company_form(form: Form[Union[UserForm, CompanyForm]]) -> dict:
+    return form.dict()
+
+
+def test_post_company_form():
+    client = TestClient(app)
+
+    # Test with UserForm
+    response = client.post(
+        "/form-union/", data={"name": "John Doe", "email": "john.doe@example.com"}
+    )
+    assert response.status_code == 200, response.text
+    assert response.json() == {
+        "received": {"name": "John Doe", "email": "john.doe@example.com"}
+    }
+
+    # Test with CompanyForm
+    response = client.post(
+        "/form-union/", data={"company_name": "Tech Corp", "industry": "Technology"}
+    )
+    assert response.status_code == 200, response.text
+    assert response.json() == {
+        "received": {"company_name": "Tech Corp", "industry": "Technology"}
+    }
+
+    # Test with mixed types
+    response = client.post(
+        "/form-union/", data={"name": "John Doe", "email": "john.doe@example.com", "company_name": "Tech Corp", "industry": "Technology"}
+    )
+    assert response.status_code == 200, response.text
+    assert response.json() == {
+        "received": {"name": "John Doe", "email": "john.doe@example.com", "company_name": "Tech Corp", "industry": "Technology"}
+    }
+
+    # Test with nested fields
+    response = client.post(
+        "/form-union/", data={"name": "John Doe", "email": "john.doe@example.com", "company_name": "Tech Corp", "industry": "Technology", "nested": {"subfield": "value"}}
+    )
+    assert response.status_code == 200, response.text
+    assert response.json() == {
+        "received": {"name": "John Doe", "email": "john.doe@example.com", "company_name": "Tech Corp", "industry": "Technology", "nested": {"subfield": "value"}}
+    }
+
+    # Test with invalid data
+    response
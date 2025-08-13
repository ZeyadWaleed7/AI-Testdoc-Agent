+
+def test_post_union_form():
+    client = TestClient(app)
+
+    # Test with a UserForm
+    response = client.post("/form-union/", json={"name": "John Doe", "email": "john.doe@example.com"})
+    assert response.status_code == 200
+    assert response.json() == {"received": {"name": "John Doe", "email": "john.doe@example.com"}}
+
+    # Test with a CompanyForm
+    response = client.post("/form-union/", json={"company_name": "Tech Innovations", "industry": "Technology"})
+    assert response.status_code == 200
+    assert response.json() == {"received": {"company_name": "Tech Innovations", "industry": "Technology"}}
+
+    # Test with a mixed form
+    response = client.post("/form-union/", json={"name": "Jane Doe", "email": "jane.doe@example.com", "company_name": "Tech Innovations", "industry": "Technology"})
+    assert response.status_code == 200
+    assert response.json() == {"received": {"name": "Jane Doe", "email": "jane.doe@example.com", "company_name": "Tech Innovations", "industry": "Technology"}}
+
+    # Test with a nested form
+    response = client.post("/form-union/", json={"name": "Alice", "email": "alice@example.com", "company_name": "Tech Innovations", "industry": "Technology", "nested": {"subfield": "Nested Value"}})
+    assert response.status_code == 200
+    assert response.json() == {"received": {"name": "Alice", "email": "alice@example.com", "company_name": "Tech Innovations", "industry": "Technology", "nested": {"subfield": "Nested Value"}}}
+
+    # Test with a nested form with a union of base models
+    response = client.post("/form-union/", json={"name": "Bob", "email": "bob@example.com", "company_name": "Tech Innovations", "industry": "Technology", "nested": {"subfield": "Nested Value"}, "base_model": {"type": "UserForm"}})
+    assert response.status_code == 200
+    assert response.json() == {"received": {"name": "Bob",
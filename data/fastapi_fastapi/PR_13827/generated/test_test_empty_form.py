}
+
+
+def test_empty_form():
+    client = TestClient(app)
+    response = client.post("/form-union/")
+    assert response.status_code == 422, response.text
+
+def test_user_form():
+    client = TestClient(app)
+    user_data = {"name": "John Doe", "email": "john.doe@example.com"}
+    response = client.post("/form-union/", data=user_data)
+    assert response.status_code == 200, response.json()
+    assert response.json()["received"] == user_data
+
+def test_company_form():
+    client = TestClient(app)
+    company_data = {"company_name": "Tech Innovations", "industry": "Technology"}
+    response = client.post("/form-union/", data=company_data)
+    assert response.status_code == 200, response.json()
+    assert response.json()["received"] == company_data
+
+def test_union_of_base_models():
+    client = TestClient(app)
+    user_data = {"name": "John Doe", "email": "john.doe@example.com"}
+    response = client.post("/form-union/", data=user_data)
+    assert response.status_code == 200, response.json()
+    assert response.json()["received"] == user_data
+
+    company_data = {"company_name": "Tech Innovations", "industry": "Technology"}
+    response = client.post("/form-union/", data=company_data)
+    assert response.status_code == 200, response.json()
+    assert response.json()["received"] == company_data
+
+    # Test with a union of base models
+    user_data = {"name": "John Doe", "email": "john.doe@example.com"}
+    response = client.post("/form-union/", data=user_data)
+    assert response.status_code == 200, response.json()
+    assert response.json()["received"] == user_data
+
+    company_data = {"company_name": "Tech Innovations", "industry": "Technology"}
+    response = client.post("/form-union/", data=company_data)
+    assert response.status_code == 200, response.json()
+    assert response.json()["received"] == company_data
+
+    # Test with a union of base models
+    user_data = {"name": "John Doe", "email":
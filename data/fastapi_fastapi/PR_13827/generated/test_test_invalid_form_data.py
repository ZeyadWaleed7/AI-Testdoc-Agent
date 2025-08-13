Union[UserForm, CompanyForm]):
+    return {"message": "Form submitted successfully"}
+
+
+def test_invalid_form_data():
+    client = TestClient(app)
+    response = client.post(
+        "/form-union/",
+        data={"name": "John", "company_name": "Tech Corp"},
+    )
+    assert response.status_code == 422, response.text
+
+    response = client.post(
+        "/form-union/",
+        data={"name": "John", "company_name": "Tech Corp", "email": "john@example.com"},
+    )
+    assert response.status_code == 422, response.text
+
+    response = client.post(
+        "/form-union/",
+        data={"name": "John", "company_name": "Tech Corp", "email": "john@example.com", "industry": "IT"},
+    )
+    assert response.status_code == 422, response.text
+
+    response = client.post(
+        "/form-union/",
+        data={"name": "John", "company_name": "Tech Corp", "email": "john@example.com", "industry": "IT", "company_name": "Tech Corp"},
+    )
+    assert response.status_code == 422, response.text
+
+    response = client.post(
+        "/form-union/",
+        data={"name": "John", "company_name": "Tech Corp", "email": "john@example.com", "industry": "IT", "company_name": "Tech Corp", "company_name": "Tech Corp"},
+    )
+    assert response.status_code == 422, response.text
+
+    response = client.post(
+        "/form-union/",
+        data={"name": "John", "company_name": "Tech Corp", "email": "john@example.com", "industry": "IT", "company_name": "Tech Corp", "company_name": "Tech Corp", "company_name": "Tech Corp"},
+    )
+    assert response.status_code == 422, response.text
+
+    response = client.post(
+        "/form-union/",
+        data={"name": "John", "company_name": "Tech Corp", "email": "john@example.com", "industry": "IT", "company_name": "Tech Corp", "company_name": "Tech Corp", "company_name
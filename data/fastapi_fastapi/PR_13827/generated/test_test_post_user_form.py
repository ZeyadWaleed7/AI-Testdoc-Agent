_name: str
+    address: str
+
+
+class EmployeeForm(BaseModel):
+    employee_id: int
+    name: str
+    position: str
+
+
+@app.post("/form-union/")
+async def post_user_form(data: Union[UserForm, CompanyForm, EmployeeForm]):
+    return {"received": data}
+
+
+def test_post_user_form():
+    client = TestClient(app)
+
+    # Test with UserForm
+    response = client.post(
+        "/form-union/", data={"name": "John Doe", "email": "john@example.com"}
+    )
+    assert response.status_code == 200, response.text
+    assert response.json() == {
+        "received": {"name": "John Doe", "email": "john@example.com"}
+    }
+
+    # Test with CompanyForm
+    response = client.post(
+        "/form-union/", data={"company_name": "TechCorp", "address": "123 Main St"}
+    )
+    assert response.status_code == 200, response.text
+    assert response.json() == {
+        "received": {"company_name": "TechCorp", "address": "123 Main St"}
+    }
+
+    # Test with EmployeeForm
+    response = client.post(
+        "/form-union/", data={"employee_id": 1, "name": "Jane Doe", "position": "Software Engineer"}
+    )
+    assert response.status_code == 200, response.text
+    assert response.json() == {
+        "received": {"employee_id": 1, "name": "Jane Doe", "position": "Software Engineer"}
+    }
+
+    # Test with mixed types
+    response = client.post(
+        "/form-union/", data={"name": "John Doe", "email": "john@example.com", "company_name": "TechCorp", "address": "123 Main St"}
+    )
+    assert response.status_code == 200, response.text
+    assert response.json() == {
+        "received": {"name": "John Doe", "email": "john@example.com", "company_name": "TechCorp", "address": "123 Main St"}
+    }
+
+    # Test with invalid data types
+    response =
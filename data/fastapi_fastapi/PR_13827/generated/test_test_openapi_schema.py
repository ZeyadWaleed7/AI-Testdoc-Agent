validate_union_form(data):
+    """
+    Validates a union form based on the provided data.
+    """
+    if not isinstance(data, dict):
+        raise ValueError("Input must be a dictionary.")
+    
+    union_form = data.get("union_form")
+    if not isinstance(union_form, dict):
+        raise ValueError("Union form must be a dictionary.")
+    
+    if "company_name" not in union_form or "industry" not in union_form:
+        raise ValueError("Union form must contain 'company_name' and 'industry'.")
+    
+    return union_form
+
+
 def get_union_form_data(union_form):
     """
     Retrieves the data for a given union form.
     """
     if not isinstance(union_form, dict):
         raise ValueError("Input must be a dictionary.")
     return union_form.get("data")

diff --git a/tests/test_union_forms.py b/tests/test_union_forms.py
new file mode 100644
index 0000000000000..e520b98e1b220
--- /dev/null
+++ b/tests/test_union_forms.py
@@ -0,0 +1 @@
+from fastapi.testclient import TestClient
+from fastapi.responses import JSONResponse
+from fastapi.exceptions import HTTPException
+import pytest
+
+def test_openapi_schema():
+    client = TestClient(app)
+    response = client.get("/openapi.json")
+    assert response.status_code == 200, response.text
+
+    assert response.json() == {
+        "openapi": "3.1.0",
+        "info": {"title": "FastAPI", "version": "0.1.0"},
+        "paths": {
+            "/form-union/": {
+                "post": {
+                    "summary": "Post Union Form",
+                    "operationId": "post_union_form_form_union__post",
+                    "requestBody": {
+                        "content": {
+                            "application/x-www-form-urlencoded": {
+                                "schema": {
+                                    "anyOf": [
+                                        {"$ref": "#/components/schemas/UserForm"},
+                                        {"$ref": "#/components/schemas/CompanyForm"},
+                                    ],
+                                    "title": "Data",
+                                }
                            }
                        },
                        "required": True,
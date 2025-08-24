[Placeholder response due to generation failure]
Generate comprehensive unit tests for this function:

def test_empty_form():
    response = client.post("/form-union/")
    assert response.status_code == 422, response.text



Diff context:
From 16228b5bc1af723106a4c7f2dfefdc69109b536d Mon Sep 17 00:00:00 2001
From: Patrick Arminio <patrick.arminio@gmail.com>
Date: Tue, 24 Jun 2025 12:14:05 +0100
Subject: [PATCH] =?UTF-8?q?=F0=9F=90=9B=20Fix=20support=20for=20unions=20w?=
 =?UTF-8?q?hen=20using=20`Form`?=
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit

---
 fastapi/dependencies/utils.py |  27 +++++-
 tests/test_union_forms.py     | 156 ++++++++++++++++++++++++++++++++++
 2 files changed, 180 insertions(+), 3 deletions(-)
 create mode 100644 tests/test_union_forms.py

diff --git a/fastapi/dependencies/utils.py b/fastapi/dependencies/utils.py
index 84dfa4d0306a6..081b63a8bdcef 100644
--- a/fastapi/dependencies/utils.py
+++ b/fastapi/dependencies/utils.py
@@ -816,6 +816,25 @@ def request_params_to_args(
     return values, errors
 
 
+def is_union_of_base_models(field_type: Any) -> bool:
+    """Check if field type is a Union where all members are BaseModel subclasses."""
+    from fastapi.types import UnionType
+
+    origin = get_origin(field_type)
+
+    # Check if it's a Union type (covers both typing.Union and types.UnionType in Python 3.10+)
+    if origin is not Union and origin is not UnionType:
+        return False
+
+    union_args = get_args(field_type)
+
+    for arg in union_args:
+        if not lenient_issubclass(arg, BaseModel):
+            return False
+
+    return True
+
+
 def _should_embed_body_fields(fields: List[ModelField]) -> bool:
     if not fields:
         return False
@@ -829,10 +848,12 @@ def _should_embed_body_fields(fields: List[ModelField]) -> bool:
     # If it explicitly specifies it is embedded, it has to be embedded
     if getattr(first_field.field_info, "embed", None):
         return True
-    # If it's a Form (or File) field, it has to be a BaseModel to be top level
+    # If it's a Form (or File) field, it has to be a BaseModel (or a union of BaseModels) to be top level
     # otherwise it has to be embedded, so that the key value pair can be extracted
-    if isinstance(first_field.field_info, params.Form) and not lenient_issubclass(
-        first_field.type_, BaseModel
+    if (
+        isinstance(first_field.field_info, params.Form)
+        and not lenient_issubclass(first_field.type_, BaseModel)
+        and not is_union_of_base_models(first_field.type_)
     ):
         return True
     return False
diff --git a/tests/test_union_forms.py b/tests/test_union_forms.py
new file mode 100644
index 0000000000000..cbe98ea825cc7
--- /dev/null
+++ b/tests/test_union_forms.py
@@ -0,0 +1,156 @@
+from typing import Union
+
+from fastapi import FastAPI, Form
+from fastapi.testclient import TestClient
+from pydantic import BaseModel
+from typing_extensions import Annotated
+
+app = FastAPI()
+
+
+class UserForm(BaseModel):
+    name: str
+    email: str
+
+
+class CompanyForm(BaseModel):
+    company_name: str
+    industry: str
+
+
+@app.post("/form-union/")
+def post_union_form(data: Annotated[Union[UserForm, CompanyForm], Form()]):
+    return {"received": data}
+
+
+client = TestClient(app)
+
+
+def test_post_user_form():
+    response = client.post(
+        "/form-union/", data={"name": "John Doe", "email": "john@example.com"}
+    )
+    assert response.status_code == 200, response.text
+    assert response.json() == {
+        "received": {"name": "John Doe", "email": "john@example.com"}
+    }
+
+
+def test_post_company_form():
+    response = client.post(
+        "/form-union/", data={"company_name": "Tech Corp", "industry": "Technology"}
+    )
+    assert response.status_code == 200, response.text
+    assert response.json() == {
+        "received": {"company_name": "Tech Corp", "industry": "Technology"}
+    }
+
+
+def test_invalid_form_data():
+    response = client.post(
+        "/form-union/",
+        data={"name": "John", "company_name": "Tech Corp"},
+    )
+    assert response.status_code == 422, response.text
+
+
+def test_empty_form():
+    response = client.post("/form-union/")
+    assert response.status_code == 422, response.text
+
+
+def test_openapi_schema():
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
+                            }
+                        },
+                        "required": True,
+                    },
+                    "responses": {
+                        "200": {
+                            "description": "Successful Response",
+                            "content": {"application/json": {"schema": {}}},
+                        },
+                        "422": {
+                            "description": "Validation Error",
+                            "content": {
+                                "application/json": {
+                                    "schema": {
+                                        "$ref": "#/components/schemas/HTTPValidationError"
+                                    }
+                                }
+                            },
+                        },
+                    },
+                }
+            }
+        },
+        "components": {
+            "schemas": {
+                "CompanyForm": {
+                    "properties": {
+                        "company_name": {"type": "string", "title": "Company Name"},
+                        "industry": {"type": "string", "title": "Industry"},
+                    },
+                    "type": "object",
+                    "required": ["company_name", "industry"],
+                    "title": "CompanyForm",
+                },
+                "HTTPValidationError": {
+                    "properties": {
+                        "detail": {
+                            "items": {"$ref": "#/components/schemas/ValidationError"},
+                            "type": "array",
+                            "title": "Detail",
+                        }
+                    },
+                    "type": "object",
+                    "title": "HTTPValidationError",
+                },
+                "UserForm": {
+                    "properties": {
+                        "name": {"type": "string", "title": "Name"},
+                        "email": {"type": "string", "title": "Email"},
+                    },
+                    "type": "object",
+                    "required": ["name", "email"],
+                    "title": "UserForm",
+                },
+                "ValidationError": {
+                    "properties": {
+                        "loc": {
+                            "items": {
+                                "anyOf": [{"type": "string"}, {"type": "integer"}]
+                            },
+                            "type": "array",
+                            "title": "Location",
+                        },
+                        "msg": {"type": "string", "title": "Message"},
+                        "type": {"type": "string", "title": "Error Type"},
+                    },
+                    "type": "object",
+                    "required": ["loc", "msg", "type"],
+                    "title": "ValidationError",
+                },
+            }
+        },
+    }

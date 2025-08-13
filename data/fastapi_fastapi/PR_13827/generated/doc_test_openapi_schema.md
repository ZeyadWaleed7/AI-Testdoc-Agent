### Documentation for the `test_openapi_schema` Function

#### **Function Purpose**
The `test_openapi_schema` function is designed to verify that the OpenAPI schema of a FastAPI application is correctly generated and validated. This function sends a GET request to the `/openapi.json` endpoint of the FastAPI application and checks if the response status code is 200, indicating a successful request.

#### **Expected Behavior**
- The function should return a JSON response with the following structure:
  ```json
  {
    "openapi": "3.1.0",
    "info": {
      "title": "FastAPI",
      "version": "0.1.0"
    },
    "paths": {
      "/form-union/": {
        "post": {
          "summary": "Post Union Form",
          "operationId": "post_union_form_form_union__post",
          "requestBody": {
            "content": {
              "application/x-www-form-urlencoded": {
                "schema": {
                  "anyOf": [
                    {"$ref": "#/components/schemas/UserForm"},
                    {"$ref": "#/components/schemas/CompanyForm"},
                  ],
                  "title": "Data",
                }
              }
            },
            "required": True,
          },
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {"application/json": {"schema": {}}},
            },
            "422": {
              "description": "Validation Error",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/HTTPValidationError"
                  }
                }
              },
            },
          },
        }
      }
    },
    "components": {
      "schemas": {
        "CompanyForm": {
          "properties": {
            "company_name": {"type": "string", "title": "Company Name"},
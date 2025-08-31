from typing import Union
from fastapi import FastAPI, Form
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing_extensions import Annotated
import inspect
from contextlib import AsyncExitStack, contextmanager
from copy import copy, deepcopy
from dataclasses import dataclass
from typing import (
import anyio
from fastapi import params
from fastapi._compat import (
from fastapi.background import BackgroundTasks
from fastapi.concurrency import (

app = FastAPI()

class UserForm(BaseModel):
    name: str
    email: str

class CompanyForm(BaseModel):
    company_name: str
    industry: str

@app.post("/form-union/")
def post_union_form(data: Annotated[Union[UserForm, CompanyForm], Form()]):
    return {"received": data}

client = TestClient(app)

def test_post_user_form():
    response = client.post(
        "/form-union/", data={"name": "John Doe", "email": "john@example.com"}
    )
    assert response.status_code == 200
    assert response.json() == {"received": {"name": "John Doe", "email": "john@example.com"}}

def test_post_company_form():
    response = client.post(
        "/form-union/", data={"company_name": "Tech Corp", "industry": "Technology"}
    )
    assert response.status_code == 200
    assert response.json() == {"received": {"company_name": "Tech Corp", "industry": "Technology"}}

def test_invalid_form_data():
    response = client.post(
        "/form-union/",
        data={"name": "John", "company_name": "Tech Corp"},
    )
    assert response.status_code == 422

def test_empty_form():
    response = client.post("/form-union/")
    assert response.status_code == 422

def test_openapi_schema():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json() == {
        "openapi": "3.1.0",
        "info": {"title": "FastAPI", "version": "0.1.0"},
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
                            "content": {"application/json": {}},
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
                        "industry": {"type": "string", "title": "Industry"},
                    },
                    "type": "object",
                    "required": ["company_name", "industry"],
                    "title": "CompanyForm",
                },
                "HTTPValidationError": {
                    "properties": {
                        "detail": {
                            "items": {
                                "anyOf": [{"type": "string"}, {"type": "integer"}]
                            },
                            "type": "array",
                            "title": "Detail",
                        },
                        "msg": {"type": "string", "title": "Message"},
                        "type": {"type": "string", "title": "Error Type"},
                    },
                    "type": "object",
                    "title": "HTTPValidationError",
                },
                "UserForm": {
                    "properties": {
                        "name": {"type": "string", "title": "Name"},
                        "email": {"type": "string", "title": "Email"},
                    },
                    "type": "object",
                    "required": ["name", "email"],
                    "title": "UserForm",
                },
                "ValidationError": {
                    "properties": {
                        "loc": {
                            "items": {
                                "anyOf": [{"type": "string"}, {"type": "integer"}]
                            },
                            "type": "array",
                            "title": "Location",
                        },
                        "msg": {"type": "string", "title": "Message"},
                        "type": {"type": "string", "title": "Error Type"},
                    },
                    "type": "object",
                    "required": ["loc", "msg", "type"],
                    "title": "ValidationError",
                },
            }
        },
    }
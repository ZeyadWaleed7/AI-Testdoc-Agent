from fastapi import FastAPI
from starlette.testclient import TestClient
from typing import Union
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

# Initialize FastAPI app
app = FastAPI()

# Define a simple route that returns a union type
@app.get("/union_type")
def read_root():
    return {"Hello": "World"}

# Define a test client
client = TestClient(app)

# Define a test function
def test_read_root():
    response = client.get("/union_type")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

# Run the test function
if __name__ == "__main__":
    test_read_root()
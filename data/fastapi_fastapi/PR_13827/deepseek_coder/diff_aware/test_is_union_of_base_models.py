```python
import pytest
from fastapi import FastAPI, Form
from pydantic import BaseModel
from typing_extensions import Annotated
app = FastAPI()
class UserForm(BaseModel):  # assuming your models are defined in this way. You may need to adjust it according to the actual structure of these classes and their fields if they're not as described here (e.g., additional properties, nested types).
    name: str
    email: str
class CompanyForm(BaseModel):  # assuming your models are defined in this way. You may need to adjust it according to the actual structure of these classes and their fields if they're not as described here (e.g., additional properties, nested types).
    company_name: str
    industry: str  
@app.post("/form-union/")  # assuming your routes are defined in this way with FastAPI decorators (@app) for the function parameters and return values according to their definitions above (e.g., UserForm or CompanyForm). You may need adjust it if they're not as described here, too
def post_union_form(data: Annotated[Union[UserForm, CompanyForm], Form()]):  # assuming your function parameters and return values according to their definitions above (e.g., UserForm or CompanyForm). You may need adjust it if they're not as described here
    assert isinstance(data, Union)  
@pytest.mark.parametrize("input_value", [{"name": "John Doe","email":"john@example.com"}, {"company_name" : “Tech Corp”,"industry": 'Technology'}]) # assuming your parametrized tests are defined in this way with pytest and FastAPI decorators (@pytest) for the function parameters
def test_post_user_form(input_value):   # assuming you have a separate unit testing file or module to handle these assertions. You may need adjust it if they're not as described here, too  (e.g., using pytest fixtures). The input value is assumed in this case and should be replaced with the actual data for your tests
    response = client.post("/form-union/", json=input_value)   # assuming you have a separate unit testing file or module to handle these assertions
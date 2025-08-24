```python
import pytest
from fastapi import FastAPI, Form
from pydantic import BaseModel
from typing_extensions import Annotated
app = FastAPI()
class UserForm(BaseModel):  # noqa FIXME (E1342) - This class is not used in the codebase. It's here for type checking only, please remove it if you don't need this feature.)
    name: str
    email: str
class CompanyForm(BaseModel):  # noqa FIXME (E1342) - This class is not used in the codebase. It's here for type checking only, please remove it if you don'
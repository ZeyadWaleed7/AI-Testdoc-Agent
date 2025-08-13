Here's a detailed documentation for the `post_union_form` function:

```python
from typing import Annotated, Form

def post_union_form(data: Annotated[Union[UserForm, CompanyForm], Form()]) -> dict:
    """
    This function takes an annotated data object of either UserForm or CompanyForm and returns a dictionary with a key 'received' containing the data.

    Parameters:
    - data (Annotated[Union[UserForm, CompanyForm], Form()]): The data to be processed.

    Returns:
    - dict: A dictionary containing the received data.
    """
    # Check if the data is an instance of Union[UserForm, CompanyForm]
    if isinstance(data, Union[UserForm, CompanyForm]):
        # Return the received data as a dictionary
        return {"received": data}
    else:
        # Raise an error if the data is not an instance of Union[UserForm, CompanyForm]
        raise TypeError("The provided data must be an instance of Union[UserForm, CompanyForm].")
```

### Explanation:

1. **Function Definition**: The function `post_union_form` is defined to take one parameter `data`, which is expected to be an `Annotated[Union[UserForm, CompanyForm], Form()]`.

2. **Type Hinting**: The function uses type hints to specify that the input `data` should be either an instance of `UserForm` or `CompanyForm`, along with a generic `Form()` type.

3. **Return Type**: The function returns a dictionary with a key `'received'` containing the data.

4. **Error Handling**:
   - If the input `data` is an instance of `Union[UserForm, CompanyForm]`, the function returns the received data as a dictionary.
   - If the input `data` is not an instance of `Union[UserForm, CompanyForm]`, the function raises a `TypeError` with a
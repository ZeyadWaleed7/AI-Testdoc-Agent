### Documentation for the `test_post_company_form` Function

#### Description
The `test_post_company_form` function is designed to test the functionality of the `/form-union/` endpoint when a POST request is made with the following parameters:
- `company_name`: The name of the company to be registered.
- `industry`: The industry in which the company is registered.

#### Expected Behavior
The function should return a JSON response with the following structure:
```json
{
    "received": {
        "company_name": "Tech Corp",
        "industry": "Technology"
    }
}
```

#### Test Cases
1. **Success Case**:
   - The function should send a POST request to `/form-union/`.
   - The request should include the required parameters: `company_name` and `industry`.
   - The response should have a status code of 200.
   - The response should contain the expected JSON object with the received company details.

2. **Error Case**:
   - The function should not send a POST request to `/form-union/`.
   - The request should not include any parameters.
   - The response should have a status code of 400.
   - The response should contain an error message indicating that the request body is missing.

3. **Missing Parameters**:
   - The function should not send a POST request to `/form-union/`.
   - The request should not include the `company_name` or `industry` parameters.
   - The response should have a status code of 400.
   - The response should contain an error message indicating that the required parameters are missing.

#### Example Code Snippet
Here's an example of how you might implement this function in Python using Flask:

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/form-union/', methods=['POST'])
def post_company_form():
    if 'company_name'
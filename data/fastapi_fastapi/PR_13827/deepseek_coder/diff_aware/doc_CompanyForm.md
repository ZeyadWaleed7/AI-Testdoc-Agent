```python
# Class Documentation 
## Description ##
The `CompanyForm` class is used to represent a form for inputting data related to companies in your application, such as company name and industry type (e.g., technology, finance). This can be useful when you want users or other parts of the system to fill out forms with information about different types of businesses that exist within an organization's network.

## Attributes ## 
- `company_name`: A string representing a company name (required)  
    - Mandatory attribute, cannot be None/empty and must not exceed maximum length defined by the system or database schema for this field in use case scenario. Maximum allowed characters is determined based on your application's specific needs such as 100 chars if you want to allow special symbols etc., otherwise it can depend upon default string max limit set up within Python/Django framework, which could be around ~256 bytes for a `str` type.
- `industry`: A string representing the industry of company (required)  
    - Mandatory attribute and cannot exceed maximum length defined by system or database schema in use case scenario as per requirement such that it can hold up to 100 characters if required, otherwise default max limit could be around ~256 bytes. It's also a mandatory field because the industry of company is not optional for every business but depends on your specific needs and requirements like technology or finance etc., so you need this attribute in case user wants more details about that particular type (like 'technology', 'finance')
  
## Methods ## 
- `__init__(company_name: str, industry:str)` : Initialize a new instance of the class. It takes two parameters - company name and its related field ie., Industry which are required to be passed while creating an object for
# scoring_api_advanced_oop


#### A request structure:
{
    "account": "@name of the company@", 
    "login": "@user name@", 
    "method": "@method name@", 
    "token": "@authtoken@", 
    "arguments": {@a dictionary with the method arguments@}
}

#### A response structure:
{
    "code": @response code@, 
    "response": {@response of the called method@}
}

{
    "code": @response code@, 
    "error": {@error message@}
}

For example,
{"code": 403, "error": "Forbidden"}



Disclaimer:
I am on trying to make the most optimum script, but rather learn advanced techniques in Python OOP

Learning advanced methods of using OOP in Python:
- descriptors 
- properties 
- meta classes

Other libraries tested:
- built-in python library optparse to parse command line arguments
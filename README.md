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

curl -X POST  -H "Content-Type: application/json" -d '{"account": "horns&hoofs", "login": "h&f", 
"method": "online_score", "token":
"55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af", "arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Стансилав",
"last_name": "Ступников", "birthday": "01.01.1990", "gender": 1}}' http://127.0.0.1:8080/method/

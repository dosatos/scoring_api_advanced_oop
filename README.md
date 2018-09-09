# scoring_api_advanced_oop  

This is a scoring json-api that: 
 - calculates score based on the arguments passed
 - generates interests based on the client id (random picking from a list)

#### Disclaimer:
The main goal of this app is to learn advanced OOP in Python
This is a part of homework given at Python Developer course, Otus.ru

#### A score request structure:
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


###### Learning advanced methods of using OOP in Python:
- descriptors 
- properties 

###### Other libraries tested:
- built-in python library optparse to parse command line arguments


##### An example of a score request: 
curl -X POST  -H "Content-Type: application/json" -d '{"account": "horns&hoofs", "login": "h&f", 
"method": "online_score", "token":
"55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af", "arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Стансилав",
"last_name": "Ступников", "birthday": "01.01.1990", "gender": 1}}' http://127.0.0.1:8080/method/

##### An example of a client interests request:
curl -X POST  -H "Content-Type: application/json" -d '{"account": "horns&hoofs", "login": "admin", 
"method": "online_score", "token":
"55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af", "arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Стансилав",
"last_name": "Ступников", "birthday": "01.01.1990", "gender": 1}}' 

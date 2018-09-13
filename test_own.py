import pytest
import hashlib

import json
import urllib2

import api
from api import ADMIN_LOGIN, ADMIN_SALT, MethodRequest


@pytest.fixture
def data():
    data = {"account": "horns&hoofs", "login": "h&f",
            "method": "online_score",
            "token":"55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af",
            "arguments": {
                "phone": "79175002040", "email": "stupnikov@otus.ru",
                "first_name": "Yeldos", "last_name": "Balgabekov",
                "birthday": "01.01.1990", "gender": 1}}
    return data


def generate_token(is_admin=False):
    if is_admin:
        return hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).hexdigest()
    else:
        return hashlib.sha512(request.account + request.login + SALT).hexdigest()

class TestMethodRequest:

    @pytest.mark.parametrize("account_name", [(""), (" "),])
    def test_account_field_can_be_nulled(self, account_name):
        data = {}
        data['account'] = account_name
        request = MethodRequest(data)
        assert 'account' not in request.invalid_fields


    def test_account_field_is_not_required(self):
        data = {}
        data['account'] = None
        request = MethodRequest(data)
        assert 'account' not in request.invalid_fields

    @pytest.mark.parametrize("login_name", [(""), (" "), ])
    def test_login_field_can_be_nulled(self, login_name):
        data = {}
        data['login'] = login_name
        request = MethodRequest(data)
        assert 'login' not in request.invalid_fields

    def test_login_field_is_required(self):
        data = {}
        data['login'] = None
        request = MethodRequest(data)
        assert 'login' in request.invalid_fields

    @pytest.mark.parametrize("token_name", [(""), (" "), ])
    def test_token_field_can_be_nulled(self, token_name):
        data = {}
        data['token'] = token_name
        request = MethodRequest(data)
        assert 'token' not in request.invalid_fields

    def test_token_field_is_required(self):
        data = {}
        request = MethodRequest(data)
        assert 'token' in request.invalid_fields

    @pytest.mark.parametrize("arguments_name", [({})])
    def test_arguments_field_can_be_nulled(self, arguments_name):
        data = {}
        data['arguments'] = arguments_name
        request = MethodRequest(data)
        assert 'arguments' not in request.invalid_fields

    def test_arguments_field_is_required(self):
        data = {}
        request = MethodRequest(data)
        assert 'arguments' in request.invalid_fields

    @pytest.mark.parametrize("method_name", [(""), (" "), ])
    def test_method_field_cannot_be_nulled(self, method_name):
        data = {}
        data['method'] = method_name
        request = MethodRequest(data)
        assert 'method' in request.invalid_fields

    def test_method_field_is_required(self):
        data = {}
        request = MethodRequest(data)
        assert 'method' in request.invalid_fields

# method = CharField(required=True, nullable=False)
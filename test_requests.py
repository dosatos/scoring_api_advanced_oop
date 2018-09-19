import pytest
import hashlib
import datetime

import api
from api import ADMIN_LOGIN, ADMIN_SALT, SALT, MethodRequest, \
    OnlineScoreRequest, ClientsInterestsRequest, Response, check_auth

from store import Store


@pytest.fixture
def data():
    data = {"account": "horns&hoofs", "login": "h&f",
            "method": "online_score",
            "token": "a_token",
            "arguments": {
                "phone": "79175002040", "email": "yeldos@balgabekov.com",
                "first_name": "Yeldos", "last_name": "Balgabekov",
                "birthday": "01.01.1990", "gender": 1}}
    return data


def generate_token(data, is_admin):
    if is_admin:
        return hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).hexdigest()
    else:
        return hashlib.sha512(data['account'] + data['login'] + SALT).hexdigest()


class TestResponse:

    def test_token_generation_for_admin_success(self, data):
        data['login'] = ADMIN_LOGIN
        data['token'] = generate_token(data, data['login'] == ADMIN_LOGIN)
        request = MethodRequest(data)
        assert check_auth(request)

    def test_token_generation_for_admin_failure(self, data):
        data['login'] = ADMIN_LOGIN
        data['token'] = "super_unique_token"
        request = MethodRequest(data)
        assert not check_auth(request)

    def test_token_generation_for_non_admin_success(self, data):
        data['token'] = generate_token(data, data['login'] == ADMIN_LOGIN)
        request = MethodRequest(data)
        assert check_auth(request)

    def test_token_generation_for_non_admin_failure(self, data):
        data['token'] = "super_unique_token"
        request = MethodRequest(data)
        assert not check_auth(request)

    @pytest.mark.parametrize("field_name, field_value, expected_response, expected_code", [
        ("account", "horns&hoofs", {'score': 5.0}, 200),
        ("method", "unknown_method", api.ERRORS[api.INVALID_REQUEST], api.INVALID_REQUEST),
    ])
    def test_method_handler_success(self, data, field_name, field_value, expected_response, expected_code):
        store = Store()
        context = None
        data['token'] = generate_token(data, data['login'] == ADMIN_LOGIN)
        data[field_name] = field_value
        method_request = MethodRequest(data)
        response = Response(method_request, context, store)
        response, code = response.get_response()
        assert response == expected_response
        assert code == expected_code

    @pytest.mark.parametrize("field_name, field_value, expected_response", [
        ("birthday", "201.10.10", "{}{}".format(api.INVALID_ARGS_MESSAGE, ", ".join(['birthday']))),
    ])
    def test_invalid_fields_response_message_is_generated_correctly(self, data, field_name, field_value, expected_response):
        store = Store()
        context = None
        data['token'] = generate_token(data, data['login'] == ADMIN_LOGIN)
        data['arguments'][field_name] = field_value
        method_request = MethodRequest(data)
        r = Response(method_request, context, store)
        response, code = r.get_response()
        assert response == expected_response
        # method_request = MethodRequest(data)
        # request = OnlineScoreRequest(method_request.arguments)
        # print "!!!" * 30, type(data['arguments']['gender']), request.invalid_fields,
        # assert  expected_response

    def test_context_is_passed_correctly(self):
        pass

    def test_final_response_is_generated_correctly(self):
        pass

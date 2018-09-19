import pytest
import hashlib
import datetime

import api
from api import ADMIN_LOGIN, ADMIN_SALT, SALT, MethodRequest, \
    OnlineScoreRequest, ClientsInterestsRequest, Response, check_auth


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

    @pytest.mark.parametrize("field_name, field_value, expected_code", [
        ("account", "horns&hoofs", 200),
        ("method", "unknown_method", api.INVALID_REQUEST),
    ])
    def test_method_handler_success(self, data, field_name, field_value, expected_code):
        store = None
        context = None
        data['token'] = generate_token(data, data['login'] == ADMIN_LOGIN)
        data[field_name] = field_value
        method_request = MethodRequest(data)
        response = Response(method_request, context, store)
        response, code = response.get_response()
        assert code == expected_code

    def test_invalid_fields(self):
        assert False

    # def test_generate_response_success(self, data):
    #     data['token'] = generate_token(MethodRequest(data))
    #     store = {
    #         "request": MethodRequest(data),
    #         "is_admin": False,
    #         "used_method": OnlineScoreRequest(data),
    #     }
    #     r = OnlineScoreRequest(data)
    #
    #     assert [r.has_first_name, r.has_last_name,
    #      r.has_birthday, r.has_gender,
    #      r.has_phone, r.has_email] == 1

        # response, code = Response(store).generate_response()
        # assert (response, code) is True


    # def test_generate_response_failure(self):
    #     pass


import pytest
import hashlib

from api import ADMIN_LOGIN, ADMIN_SALT, SALT, MethodRequest, OnlineScoreRequest, ClientsInterestsRequest, Response


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


def generate_token(request):
    if request.is_admin:
        return hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).hexdigest()
    else:
        return hashlib.sha512(request.account + request.login + SALT).hexdigest()



class TestMethodRequest:

    @pytest.mark.parametrize("account_name", [(""), (" "),])
    def test_account_field_can_be_nulled(self, account_name):
        data = {'account': account_name}
        request = MethodRequest(data)
        assert 'account' not in request.invalid_fields


    def test_account_field_is_not_required(self):
        data = {}
        request = MethodRequest(data)
        assert 'account' not in request.invalid_fields

    @pytest.mark.parametrize("login_name", [(""), (" "), ])
    def test_login_field_can_be_nulled(self, login_name):
        data = {'login': login_name}
        request = MethodRequest(data)
        assert 'login' not in request.invalid_fields

    def test_login_field_is_required(self):
        data = {}
        request = MethodRequest(data)
        assert 'login' in request.invalid_fields

    @pytest.mark.parametrize("token_name", [(""), (" "), ])
    def test_token_field_can_be_nulled(self, token_name):
        data = {'token': token_name}
        request = MethodRequest(data)
        assert 'token' not in request.invalid_fields

    def test_token_field_is_required(self):
        data = {}
        request = MethodRequest(data)
        assert 'token' in request.invalid_fields

    @pytest.mark.parametrize("arguments_name", [({})])
    def test_arguments_field_can_be_nulled(self, arguments_name):
        data = {'arguments': arguments_name}
        request = MethodRequest(data)
        assert 'arguments' not in request.invalid_fields

    def test_arguments_field_is_required(self):
        data = {}
        request = MethodRequest(data)
        assert 'arguments' in request.invalid_fields

    @pytest.mark.parametrize("method_name", [(""), (" "), ])
    def test_method_field_cannot_be_nulled(self, method_name):
        data = {'method': method_name}
        request = MethodRequest(data)
        assert 'method' in request.invalid_fields

    def test_method_field_is_required(self):
        data = {}
        request = MethodRequest(data)
        assert 'method' in request.invalid_fields

    @pytest.mark.parametrize("value", [ADMIN_LOGIN])
    def test_is_admin_property_success(self, value):
        data = {'login': value}
        request = MethodRequest(data)
        assert request.is_admin is True

    @pytest.mark.parametrize("value", ["Yeldos123"])
    def test_is_admin_property_failure(self, value):
        data = {'login': value}
        request = MethodRequest(data)
        assert request.is_admin is False



class TestOnlineScoreRequest:

    @pytest.mark.parametrize("first_name", [(""), (" "), ])
    def test_first_name_field_can_be_nulled(self, first_name):
        arguments = {'first_name': first_name}
        request = OnlineScoreRequest(arguments)
        assert 'first_name' not in request.invalid_fields

    def test_first_name_field_is_required(self):
        arguments = {}
        request = OnlineScoreRequest(arguments)
        assert 'first_name' not in request.invalid_fields

    @pytest.mark.parametrize("last_name", [(""), (" "), ])
    def test_last_name_field_can_be_nulled(self, last_name):
        arguments = {'last_name': last_name}
        request = OnlineScoreRequest(arguments)
        assert 'last_name' not in request.invalid_fields

    def test_last_name_field_is_required(self):
        arguments = {}
        request = OnlineScoreRequest(arguments)
        assert 'last_name' not in request.invalid_fields

    @pytest.mark.parametrize("email", [(""), (" "), ])
    def test_email_field_can_be_nulled(self, email):
        arguments = {'email': email}
        request = OnlineScoreRequest(arguments)
        assert 'email' not in request.invalid_fields

    def test_email_field_is_required(self):
        arguments = {}
        request = OnlineScoreRequest(arguments)
        assert 'email' not in request.invalid_fields

    @pytest.mark.parametrize("phone", [(""), (" "), ])
    def test_phone_field_can_be_nulled(self, phone):
        arguments = {'phone': phone}
        request = OnlineScoreRequest(arguments)
        assert 'phone' not in request.invalid_fields

    def test_phone_field_is_required(self):
        arguments = {}
        request = OnlineScoreRequest(arguments)
        assert 'phone' not in request.invalid_fields

    @pytest.mark.parametrize("birthday", [(""), (" "), ])
    def test_birthday_field_can_be_nulled(self, birthday):
        arguments = {'birthday': birthday}
        request = OnlineScoreRequest(arguments)
        assert 'birthday' not in request.invalid_fields

    def test_birthday_field_is_required(self):
        arguments = {}
        request = OnlineScoreRequest(arguments)
        assert 'birthday' not in request.invalid_fields

    @pytest.mark.parametrize("gender", [(0), ])
    def test_gender_field_can_be_nulled(self, gender):
        arguments = {'gender': gender}
        request = OnlineScoreRequest(arguments)
        assert 'gender' not in request.invalid_fields

    def test_gender_field_is_required(self):
        arguments = {}
        request = OnlineScoreRequest(arguments)
        assert 'gender' not in request.invalid_fields

    @pytest.mark.parametrize("value", ["Yeldos", "Dima"])
    def test_has_first_name_field_success(self, value):
        arguments = {'first_name': value}
        request = OnlineScoreRequest(arguments)
        assert request.has_first_name is True

    @pytest.mark.parametrize("value", ["", None])
    def test_has_first_name_field_failure(self, value):
        arguments = {'first_name': value}
        request = OnlineScoreRequest(arguments)
        assert request.has_first_name is False

    @pytest.mark.parametrize("value", ["Yeldos", "Dima"])
    def test_has_last_name_field_success(self, value):
        arguments = {'last_name': value}
        request = OnlineScoreRequest(arguments)
        assert request.has_last_name is True

    @pytest.mark.parametrize("value", ["", None])
    def test_has_last_name_field_failure(self, value):
        arguments = {'last_name': value}
        request = OnlineScoreRequest(arguments)
        assert request.has_last_name is False

    @pytest.mark.parametrize("value", ["Yeldos@gmail.com", "Dima@yahoo.com"])
    def test_has_email_field_success(self, value):
        arguments = {'email': value}
        request = OnlineScoreRequest(arguments)
        assert request.has_email is True

    @pytest.mark.parametrize("value", ["", None])
    def test_has_email_field_failure(self, value):
        arguments = {'email': value}
        request = OnlineScoreRequest(arguments)
        assert request.has_email is False

    @pytest.mark.parametrize("value", ["77059997044", "79069997044"])
    def test_has_phone_field_success(self, value):
        arguments = {'phone': value}
        request = OnlineScoreRequest(arguments)
        assert request.has_phone is True

    @pytest.mark.parametrize("value", ["", None])
    def test_has_phone_field_failure(self, value):
        arguments = {'phone': value}
        request = OnlineScoreRequest(arguments)
        assert request.has_phone is False

    @pytest.mark.parametrize("value", ["77059997044", "79069997044"])
    def test_has_birthday_field_success(self, value):
        arguments = {'birthday': value}
        request = OnlineScoreRequest(arguments)
        assert request.has_birthday is True

    @pytest.mark.parametrize("value", ["", None])
    def test_has_birthday_field_failure(self, value):
        arguments = {'birthday': value}
        request = OnlineScoreRequest(arguments)
        assert request.has_birthday is False

    @pytest.mark.parametrize("value", ["77059997044", "79069997044"])
    def test_has_gender_field_success(self, value):
        arguments = {'gender': value}
        request = OnlineScoreRequest(arguments)
        assert request.has_gender is True



class TestClientInterestRequest:

    def test_client_ids_field_is_required(self):
        arguments = {}
        request = ClientsInterestsRequest(arguments)
        assert 'client_ids' in request.invalid_fields

    @pytest.mark.parametrize("date", [(""), (" "), ])
    def test_date_field_can_be_nulled(self, date):
        arguments = {'date': date}
        request = ClientsInterestsRequest(arguments)
        assert 'date' not in request.invalid_fields

    def test_date_field_is_required(self):
        arguments = {}
        request = ClientsInterestsRequest(arguments)
        assert 'date' not in request.invalid_fields

    @pytest.mark.parametrize("value", [[1, 2, 3], [1]])
    def test_has_client_ids_field_success(self, value):
        arguments = {'client_ids': value}
        request = ClientsInterestsRequest(arguments)
        assert request.has_client_ids is True

    @pytest.mark.parametrize("value", [[]])
    def test_has_client_ids_field_failure(self, value):
        arguments = {'client_ids': value}
        request = ClientsInterestsRequest(arguments)
        assert request.has_client_ids is False

    @pytest.mark.parametrize("value", ["12.12.1989"])
    def test_has_date_field_success(self, value):
        arguments = {'date': value}
        request = ClientsInterestsRequest(arguments)
        assert request.has_date is True

    @pytest.mark.parametrize("value", [""])
    def test_has_date_field_failure(self, value):
        arguments = {'date': value}
        request = ClientsInterestsRequest(arguments)
        assert request.has_date is False



# class TestResponse:
#
#     def test_generate_response_success(self, data):
#         data['token'] = generate_token(MethodRequest(data))
#         store = {
#             "request": MethodRequest(data),
#             "is_admin": False,
#             "used_method": OnlineScoreRequest(data),
#         }
#         r = OnlineScoreRequest(data)
#
#         assert [r.has_first_name and r.has_last_name,
#          r.has_birthday and r.has_gender,
#          r.has_phone and r.has_email] == 1
#
#         # response, code = Response(store).generate_response()
#         # assert (response, code) is True
#
#
#     def test_generate_response_failure(self):
#         pass


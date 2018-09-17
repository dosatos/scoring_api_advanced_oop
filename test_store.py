import pytest
from store import Store
import hashlib
import datetime

from api import ADMIN_LOGIN, ADMIN_SALT, SALT, MethodRequest, \
    OnlineScoreRequest, ClientsInterestsRequest, Response, check_auth


@pytest.fixture
def data():
    data = {"account": "horns&hoofs", "login": "h&f",
            "method": "online_score",
            "token":"55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af",
            "arguments": {
                "phone": "79175002040", "email": "yeldos@balgabekov.com",
                "first_name": "Yeldos", "last_name": "Balgabekov",
                "birthday": "01.01.1990", "gender": 1}}
    return data



class TestStore:

    @pytest.mark.parametrize("kval_pair, result", [
        (("hello", "world"), "world"),
        (("dictionary", '{"name": "yeldos"}'), '{"name": "yeldos"}')
    ])
    def test_get_set_store_success(self, kval_pair, result):
        s = Store()
        key, val = kval_pair
        s.set(key, val)
        assert s.get(key) == result

    @pytest.mark.xfail(raises=TypeError)
    @pytest.mark.parametrize("kval_pair, result", [
        (("hello", ["world"]), ["world"]),
        (("hello", 100), 100),
    ])
    def test_get_set_store_failure(self, kval_pair, result):
        s = Store()
        key, val = kval_pair
        s.set(key, val)

    @pytest.mark.parametrize("kval_pair, result", [
        (("hello", "world"), "world"),
        (("dictionary", '{"name": "yeldos"}'), '{"name": "yeldos"}')
    ])
    def test_get_set_store_success(self, kval_pair, result):
        s = Store()
        key, val = kval_pair
        s.set(key, val)
        assert s.get(key) == result




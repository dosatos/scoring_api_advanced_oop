import pytest
from store import Store
import time
from scoring import get_score, get_interests
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


@pytest.fixture
def s():
    return Store()



class TestGetScore:


    @pytest.mark.parametrize("id_data_pair, duration, result", [
        (("uid:hello", "world"), 60*60, "world"),
        (("i:cidhello", '{"interests": ["hello", "world"]}'), 60*60, '{"interests": ["hello", "world"]}')
    ])
    def test_cache_get_set_store_success(self, s, id_data_pair, duration, result):
        idx, data = id_data_pair
        s.cache_set(idx, data, duration)
        assert s.cache_get(idx) == result
        s.delete(idx)

    @pytest.mark.parametrize("id_data_pair, duration, result", [
        (("uid:hello", "world"), 60 * 60, "world"),
        (("i:cidhello", '{"interests": ["hello", "world"]}'), 60 * 60, '{"interests": ["hello", "world"]}')
    ])
    def test_cache_delete_store_success(self, s, id_data_pair, duration, result):
        idx, data = id_data_pair
        s.cache_set(idx, data, duration)
        assert s.cache_get(idx) == result
        s.delete(idx)
        assert s.cache_get(idx) is None

    @pytest.mark.parametrize("id_data_pair, duration, pause, result", [
        (("uid:hello", "world"), 1, 0, "world"),
        (("i:cidhello", '{"interests": ["hello", "world"]}'), 1, 1.1, None)
    ])
    def test_cache_set_expiry_time(self, s, id_data_pair, duration, pause, result):
        idx, data = id_data_pair
        s.cache_set(idx, data, duration)
        time.sleep(pause)
        assert s.cache_get(idx) == result

    @pytest.mark.parametrize("phone, email, first_name, last_name, birthday, gender, result", [
        ("79175002040", "yeldos@balgabekov.com", "Yeldos", "Balgabekov", datetime.datetime(2017, 01, 31), 1, 5),
        ("79175002040", "", "Yeldos", "Balgabekov", datetime.datetime(2017, 01, 31), 1, 3.5),
        ("", "yeldos@balgabekov.com", "Yeldos", "Balgabekov", datetime.datetime(2017, 01, 31), 1, 3.5),
        ("", "", "Yeldos", "Balgabekov", datetime.datetime(2017, 01, 31), 1, 2),
        ("79175002040", "yeldos@balgabekov.com", "Yeldos", "", datetime.datetime(2017, 01, 31), 1, 4.5),
        ("79175002040", "yeldos@balgabekov.com", "", "Balgabekov", datetime.datetime(2017, 01, 31), 1, 4.5),
        ("79175002040", "yeldos@balgabekov.com", "Yeldos", "Balgabekov", None, 1, 3.5),
        ("79175002040", "yeldos@balgabekov.com", "Yeldos", "Balgabekov", datetime.datetime(2017, 01, 31), "", 3.5),
        ("79175002040", "yeldos@balgabekov.com", "Yeldos", "Balgabekov", None, None, 3.5),
        ("", "", "", "", None, None, 0),
    ])
    def test_get_score(self, s, phone, email, birthday, gender, first_name, last_name, result):
        calc_score = get_score(s, phone, email, birthday, gender, first_name, last_name)
        assert calc_score == result

        key_parts = [
            first_name or "",
            last_name or "",
            birthday.strftime("%Y%m%d") if birthday is not None else "",
        ]
        key = "uid:" + hashlib.md5("".join(key_parts)).hexdigest()

        s.delete(key)


class TestGetInterests:

    @pytest.mark.parametrize("cid, value, result", [
        ("hello", '["value"]', ["value"]),
        ("hello", '{"value": "name"}', {"value": "name"}),
    ])
    def test_get_interests_success(self, s, cid, value, result):
        s.cache_set("i:%s" % cid, value)
        assert get_interests(s, cid) == result
        s.delete("i:%s" % cid)



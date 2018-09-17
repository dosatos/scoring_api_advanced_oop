import redis


class Store(object):
    def __init__(self):
        self.conn = redis.StrictRedis(host='localhost', port=6379, db=0)

    def get(self, key):
        return self.conn.get(key)

    def set(self, key, val):
        if isinstance(val, str):
            self.conn.set(key, val)
        elif isinstance(val, dict):
            self.conn.hmset(key, val)
        else:
            raise TypeError

    def cache_get(self, key):
        return self.conn.hget("cache", key)


# data = {"account": "horns&hoofs", "login": "h&f",
#             "method": "online_score",
#             "token":"55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af",
#             "arguments": {
#                 "phone": "79175002040", "email": "yeldos@balgabekov.com",
#                 "first_name": "Yeldos", "last_name": "Balgabekov",
#                 "birthday": "01.01.1990", "gender": 1}}



# r = redis.StrictRedis(host='localhost', port=6379, db=0)



#
# r.hmset('foo', data)
#
# print r.hmget('foo', 'account')
# print r.hget('foo', 'account')
# print r.hgetall('foo')
#

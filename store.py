import redis
import time
import functools


def connection_time_out(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for _ in range(5):
            try:
                return func(*args, **kwargs)
            except redis.ConnectionError:
                time.sleep(5)
            raise redis.ConnectionError
    return wrapper


class Store(object):
    def __init__(self):
        self.conn = redis.StrictRedis(host='localhost', port=6379, db=0)

    @connection_time_out
    def get(self, key):
        return self.conn.get(key)

    @connection_time_out
    def cache_get(self, key):
        return self.conn.get(key)

    @connection_time_out
    def cache_set(self, key, val, duration=60*60):
        if isinstance(val, (str, float)) or val == 0:
            self.conn.setex(key, duration, val)
        elif isinstance(val, dict):
            self.conn.hmsetex(key, val)
            self.conn.expire(key, duration)
        else:
            raise TypeError

    @connection_time_out
    def delete(self, key):
        self.conn.delete(key)

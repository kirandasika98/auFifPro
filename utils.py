""""
App utilities in this file
"""
import time
import sys
import json


TWO_DAYS = 172800

class MyMemcache():
    def __init__(self, conn=None):
        self.conn = conn

    def set(self, key, value):
        self.conn.set(key, self.serialize_protocol(value),
                    time=(int(time.time()) + TWO_DAYS),
                    compress_level=0)

    def get(self, key):
        """
        args:
            key in the memcache server
        return:
            object of memcache data or None if nothing is there
        """
        value = self.conn.get(key)
        if value is not None:
            return json.loads(value)["data"]

        return None

    def delete(self, key):
        return self.conn.delete(key)

    def serialize_protocol(self, value):
        """
        args:
            value: generally a dict with data to be cached
        return:
            serialized format of the data to be cached

        Custom JSON serialization prtocol markup
        {
            "expiry_timestamp": "UNIX_SECOND_TIMESTAMP",
            "data": {
                "foo": "bar",
                .
                .
                .
            }
        },
        "buff_size": "SIZE_OF_OBJECT"
        """
        return json.dumps(dict(expiry_timestamp=(int(time.time()) + TWO_DAYS),
                                data=value, buff_size=sys.getsizeof(value)))

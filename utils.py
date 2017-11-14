""""
App utilities in this file
"""
import time
import sys
import json
import requests


TWO_DAYS = 172800
API_BASE_URL = "https://api.mailgun.net/v3/{}/messages" # {} for mailgun domain

class MyMemcache(object):
    """
    Memcache wrapper
    """
    def __init__(self, conn=None):
        self.conn = conn

    def set(self, key, value):
        """
        Set a new memcache key and value
        """
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
        """
        Deletes the specifies memcache key
        """
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


class MailGunHandler(object):
    """
    Mailgun handler
    """
    def __init__(self, api_key, mailgun_domain):
        self.api_key = api_key
        self.mailgun_domain = mailgun_domain

    def service_url(self):
        """
        returns service api url
        """
        return API_BASE_URL.format(self.mailgun_domain)

    def send_email(self, to_email, subject, body):
        """
        send a request to the mailgun api for email to be sent.
        """
        res = requests.post(
            self.service_url(),
            auth=("api", self.api_key),
            data={
                "from": "AuFifPro <no-reply@{}>".format(self.mailgun_domain),
                "to": [to_email, self.mailgun_domain],
                "subject": subject,
                "text": body
            }
        )
        return res

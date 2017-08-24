#-*- coding: utf-8 -*-

"""
this backend requires the plivo python library: https://pypi.python.org/pypi/plivo/
"""


from plivo import RestAPI


from django.conf import settings
from sendsms.backends.base import BaseSmsBackend

PLIVO_ACCOUNT_SID = getattr(settings, 'SENDSMS_PLIVO_ACCOUNT_SID', '')
PLIVO_AUTH_TOKEN = getattr(settings, 'SENDSMS_PLIVO_AUTH_TOKEN', '')


class SmsBackend(BaseSmsBackend):
    def send_messages(self, messages):
        client = RestAPI(PLIVO_ACCOUNT_SID, PLIVO_AUTH_TOKEN)
        for message in messages:
            for to in message.to:
                try:
                    params = {
                        'src': to,
                        'dst': message.from_phone,
                        'text' : message.body
                    }
                    client.send_message(params)

                except:
                    if not self.fail_silently:
                        raise

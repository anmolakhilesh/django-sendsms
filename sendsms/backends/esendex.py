# -*- coding: utf-8 -*-
"""
Esendex sms gateway backend. (http://www.esendex.es/)

Configuration example.
~~~~~~~~~~~~~~~~~~~~~~

Modify your settings.py::
    
    ESENDEX_USERNAME = 'yourusername'
    ESENDEX_PASSWORD = 'mysecretpassword'
    ESENDEX_ACCOUNT = 'account-key-provided-by-esendex'
    ESENDEX_SANDBOX = False # True if yo like test first
    INSTALLED_APPS += ['sendsms']

Usage::
    
    from sendsms.message import SmsMessage
    message = SmsMessage(
        body = 'my 160 chars sms',
        from_phone = '111111111',
        to = ['222222222']
    )
    message.send()
"""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_unicode

import requests

from .base import BaseSmsBackend

ESENDEX_API_URL = 'https://www.esendex.com/secure/messenger/formpost/SendSMS.aspx'
ESENDEX_USERNAME = getattr(settings, 'ESENDEX_USERNAME', '')
ESENDEX_PASSWORD = getattr(settings, 'ESENDEX_PASSWORD', '')
ESENDEX_ACCOUNT = getattr(settings, 'ESENDEX_ACCOUNT', '')
ESENDEX_SANDBOX = getattr(settings, 'ESENDEX_SANDBOX', False)

class SmsBackend(BaseSmsBackend):
    """ 
    SMS Backend for esendex.es provider.
    """

    def _parse_response(self, response):
        """
        Parse http raw respone into python
        dictionary object.
        
        :param str response: http response
        :returns: response dict
        :rtype: dict
        """

        response_dict = {}
        for line in response.splitlines():
            key, value = response.split("=", 1)
            response_dict[key] = value
        return response_dict

    def _send(self, message):
        """
        Private method for send one message.

        :param SmsMessage message: SmsMessage class instance.
        :returns: True if message is sended else False
        :rtype: bool
        """

        params = {
            'EsendexUsername': ESENDEX_USERNAME,
            'EsendexPassword': ESENDEX_PASSWORD,
            'EsendexAccount': ESENDEX_ACCOUNT, 
            'EsendexOriginator': message.from_phone, 
            'EsendexRecipient': ",".join(message.to),
            'EsendexBody': message.body,
            'EsendexPlainText':'1'
        }
        if ESENDEX_SANDBOX:
            params['EsendexTest'] = '1'

        response = requests.post(ESENDEX_API_URL, params)
        if response.status_code != 200:
            if not self.fail_silently:
                raise
            else:
                return False
        
        if not response.content.startswith('Result'):
            if not self.fail_silently:
                raise
            else: 
                return False

        response = self._parse_response(response.content)
        if ESENDEX_SANDBOX and response['Result'] == 'Test':
            return True
        else:
            if response['Result'] == 'OK':
                return True
            else:
                if not self.fail_silently:
                    raise
        
        return False

    def send_messages(self, messages):
        """
        Send messages.

        :param list messages: List of SmsMessage instences.
        :returns: number of messages seded succesful.
        :rtype: int
        """
        counter = 0
        for message in messages:
            res = self._send(message)
            if res:
                counter += 1

        return counter
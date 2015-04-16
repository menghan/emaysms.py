#!/usr/bin/env python

import logging
from urllib2 import urlopen, URLError
from urllib import urlencode
import xml.etree.ElementTree as ET

ENDPOINT_URL = 'http://sdkhttp.eucp.b2m.cn/sdkproxy/'
SDK_VERSION = '4.1.0'


class EmaySMSException(Exception):
    pass


class EmaySMS(object):

    def __init__(self, cdkey, password):
        self.cdkey = cdkey
        self.password = password

    def api(self, action, data):
        data['cdkey'] = self.cdkey
        data['password'] = self.password

        try:
            f = urlopen(ENDPOINT_URL + action + '.action', urlencode(data))
            xml = f.read().strip()
        except URLError as e:
            raise EmaySMSException(e)

        try:
            e = ET.fromstring(xml)
            err = int(e.find('error').text)
            msg = e.find('message').text
        except ET.ParseError as e:
            raise EmaySMSException(e)

        if 1 == err:    # Something went wrong
            raise EmaySMSException(msg)
        else:           # Looks good
            return msg

    def register(self):
        '''
        Register the cdkey once and for all. A cdkey must be registered before
        you can use it to send SMS. A cdkey needs to be re-registered if it is
        de-registered before.
        '''

        self.api('regist', {})

    def deregister(self):
        ' De-register a cdkey '
        self.api('logout', {})

    def register_detail_info(self, cdkey, password, name, contact, tel,
                             mobile, email, fax, address, zipcode):
        ' Register your company\'s detailed information. '

        self.api('registdetailinfo', {
            'ename': name,
            'linkman': contact,  # I HATE POOR ENGLISH!!! WTF is linkman??
            'phonenum': tel,
            'mobile': mobile,
            'email': email,
            'fax': fax,
            'address': address,
            'postcode': zipcode
        })

    def send(self, phone_numbers, message, time=None, serial=None):
        ' Send an instant SMS to a list of phone numbers '

        if not isinstance(message, unicode):
            raise EmaySMSException('Message must be a Unicode string. ')

        # Max 500 chars (same for UTF-8 and ASCII) per message. It will be
        # split into 70 chars chunks before sending to mobile phones. The 4.1.0
        # HTTP SDK is wrong about the 1,000 chars limit for ASCII chars.
        if len(message) > 500:
            raise EmaySMSException('Message too long. ')

        numbers = ','.join(phone_numbers)
        msg = message.encode('utf-8')
        logging.debug('{0} | "{1}"'.format(numbers, msg))
        data = {'phone': numbers, 'message': msg}

        if time is None:
            action = 'sendsms'
            if len(phone_numbers) > 1000:
                raise EmaySMSException('Too many phone numbers. '
                                       'Maxium 1000 for sending instant SMS. ')
        else:
            action = 'sendtimesms'
            data['sendtime'] = time
            if len(phone_numbers) > 200:
                raise EmaySMSException('Too many phone numbers. '
                                       'Maxium 200 for sending timed SMS. ')

        if serial is not None:
            if len(serial) > 10:
                raise EmaySMSException('Serial too long. Max 10 digits. ')
            data['addserial'] = serial

        self.api(action, data)

    @property
    def sent(self):
        return self.api('getmo', {})

    @property
    def balance(self):
        ' Query account blance in RMB '
        msg = self.api('querybalance', {})
        return float(msg)

    def recharge(self, card_number, card_password):
        ' Recharge account using a prepaid card '
        self.api('chargeup', {'cardno': card_number, 'cardpass': card_password})

    def change_password(self, new_password):
        self.api('changepassword', {'newPassword': new_password})

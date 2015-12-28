#! /usr/bin/env python3

"""
This file is part of Pybakalib.

Pybakalib is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Foobar is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Pybakalib.  If not, see <http://www.gnu.org/licenses/>.
"""




import xml.etree.ElementTree as ET
import base64
import hashlib
import urllib.request
import urllib.parse
import datetime

from . import marks

class BakaURL(object):
    @staticmethod
    def fix_url(url: str) -> str:
        if not url.startswith('http'):
            url = 'http://' + url
        if not url.endswith('/'):
            url = url + '/'
        return url


class LoginError(Exception):
    pass

class BakaAccount(object):
    def __init__(self, url, username=None, password=None, prehash=None):
        self.url = BakaURL.fix_url(url)
        self.account_details = None

        if prehash != None:
            self.token = self.get_hash_level_2(prehash)
        elif username != None and password != None:
            self.username = username
            self.password = password

            self.token = self.get_hash_level_2(self.get_hash_level_1(username, password))
        else:
            raise AttributeError('Invalid arguments')

    """
    Acquires salt from server. The salt consists of 3 parts (details in code).
     It is downloaded by HTTP GET request:
    http(s)://[ROOT OF BAKALARI WEB SERVICE]/login.aspx?gethx=[USERNAME]
    """
    def get_salt(self, username):
        try:
            salt_xml = self.get_resource({'gethx': username})
            res = ET.fromstring(salt_xml)
            salt = res.find('salt').text + res.find('ikod').text + res.find('typ').text
            return salt
        except:
            raise LoginError('URL or username invalid')

    def get_resource(self, params):
        with urllib.request.urlopen(self.url + 'login.aspx?' + urllib.parse.urlencode(params)) as req:
            return req.read().decode('utf8')

    """
    Level 1 hash is useful for storing because the password is not obvious from
     it but it is possible to log in with it. It is composed of an username and
     hashed password with salt.
    This hash is stored by Android application in its config files.
    """
    def get_hash_level_1(self, username, password):
        passw = (self.get_salt(username) + password).encode('utf8')
        ha = base64.urlsafe_b64encode(hashlib.sha512(passw).digest())
        return '*login*' + username + '*pwd*' + ha.decode('utf8') + '*sgn*ANDR'

    """
    Level 2 hash is used for actual log in process. It is generated from level 1
     hash and current date.
    """
    def get_hash_level_2(self,prehash):
        now = datetime.datetime.now()
        date = '{:04}{:02}{:02}'.format(now.year,now.month,now.day)
        l2 = hashlib.sha512((prehash + date).encode('utf8')).digest()
        return base64.urlsafe_b64encode(l2).decode('utf8')

    """
    Returns basic information about the account. The main thing here is list of
     available modules that can be worked with later.
    """
    def get_account_details(self):
        if self.account_details != None:
            return self.account_details
        else:
                try:
                    login_xml = self.get_resource({'hx':self.token, 'pm':'login'})
                    root = ET.fromstring(login_xml)
                    if root.find('result').text != '01':
                        raise LoginError('Wrong password.')
                    data = {
                        'name': root.find('jmeno').text,
                        'modules': list(filter(lambda x: len(x) > 0,root.find('moduly').text.split('*'))),
                        'school': root.find('skola').text,
                        'system_version' : root.find('verze').text
                    }
                    self.account_details = data
                    return self.account_details
                except ParseError as orig:
                    raise ConnectionError('Response from server was invalid. Try again.') from orig

    def get_module_xml(self, name):
        if name in self.get_account_details()['modules']:
            return self.get_resource({'pm':name, 'hx':self.token})
        else:
            raise Exception('Server does not support operation - ' + name )
    def get_marks(self):
        return marks.MarksModule(self.get_module_xml('znamky'),self.get_module_xml('predvidac'))

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

class BakaAccount:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    """
    Acquires salt from server. The salt consists of 3 parts (details in code).
     It is downloaded by HTTP GET request:
    http(s)://[ROOT OF BAKALARI WEB SERVICE]/login.aspx?gethx=[USERNAME]
    """
    def get_salt(self):
        try:
            salt_xml = self.get_resource({'gethx':self.username})
            res = ET.fromstring(salt_xml)
            salt = res.find('salt').text + res.find('ikod').text + res.find('typ').text
            return salt
        except:
            raise Exception('URL or username invalid')

    def get_resource(self, params):
        with urllib.request.urlopen(self.url + 'login.aspx?' + urllib.parse.urlencode(params)) as req:
            return req.read().decode('utf8')

    """
    Level 1 hash is useful for storing because the password is not obvious from
     it but it is possible to log in with it. It is composed of an username and
     hashed password with salt.
    This hash is stored by Android application in its config files.
    """
    def get_hash_level_1(self):
        passw = (self.get_salt() + self.password).encode('utf8')
        ha = base64.urlsafe_b64encode(hashlib.sha512(passw).digest())
        return '*login*' + self.username + '*pwd*' + ha.decode('utf8') + '*sgn*ANDR'

    """
    Level 2 hash is used for actual log in process. It is generated from level 1
     hash and current date.
    """
    def get_hash_level_2(self,l1=None):
        now = datetime.datetime.now()
        date = '{:04}{:02}{:02}'.format(now.year,now.month,now.day)
        if l1 == None:
            l1 = self.get_hash_level_1()
        l2 = hashlib.sha512((l1 + date).encode('utf8')).digest()
        return base64.urlsafe_b64encode(l2).decode('utf8')

    """
    Returns basic information about the account. The main thing here is list of
     available modules that can be worked with later.
    """
    def get_account_details(self):
        login_xml = self.get_resource({'hx':self.get_hash_level_2(),'pm':'login'})
        print(login_xml)
        root = ET.fromstring(login_xml)
        data = {
            'name': root.find('jmeno').text,
            'modules': list(filter(lambda x: len(x) > 0,root.find('moduly').text.split('*'))),
            'school': root.find('skola').text,
            'system_version' : root.find('verze').text
        }
        return data

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
import datetime

class LoginError(Exception):
    pass

def get_token(client, *args):
    if len(args) == 1:
        return _get_hash_level_2(args[0])

    elif len(args) == 2:
        username = args[0]
        password = args[1]

        salt = _get_salt(client, username)

        if salt is None:
            return None

        hash_level_1 = _get_hash_level_1(username, password, salt)
        hash_level_2 = _get_hash_level_2(hash_level_1)
        return hash_level_2
    else:
        raise AttributeError('Invalid argument count. Expected 1 or 2 arguments.')


def _get_salt(client, username):
    """
    Acquires salt from server.
     It is downloaded by HTTP GET request:
    http(s)://[ROOT OF BAKALARI WEB SERVICE]/login.aspx?gethx=[USERNAME]

    @returns salt or None, when username does not exist
    """
    try:
        salt_xml = client.get_resource({'gethx': username})
        res = ET.fromstring(salt_xml)
        salt = res.find('salt').text + res.find('ikod').text + res.find('typ').text
        return salt
    except ET.ParseError:
        return None


def _get_hash_level_1(username, password, salt):
    """
    Level 1 hash is useful for storing because the password is not obvious from
     it but it is possible to log in with it. It is composed of an username and
     hashed password with salt.
    This hash is stored by Android application in its config files.
    """
    passw = (salt + password).encode('utf8')
    ha = base64.urlsafe_b64encode(hashlib.sha512(passw).digest())
    return '*login*' + username + '*pwd*' + ha.decode('utf8') + '*sgn*ANDR'


def _get_hash_level_2(hash_level_1):
    """
    Level 2 hash is used for actual log in process. It is generated from level 1
     hash and current date.
    """
    now = datetime.datetime.now()
    date = '{:04}{:02}{:02}'.format(now.year,now.month,now.day)
    l2 = hashlib.sha512((hash_level_1 + date).encode('utf8')).digest()
    return base64.urlsafe_b64encode(l2).decode('utf8')

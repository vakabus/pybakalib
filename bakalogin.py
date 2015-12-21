#! /usr/bin/env python3

import xml.etree.ElementTree as ET
import base64
import hashlib
import urllib.request
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
        with urllib.request.urlopen(self.url + 'login.aspx?gethx=' + self.username) as req:
            res = ET.fromstring(req.read())
            salt = res.find('salt').text + res.find('ikod').text + res.find('typ').text
            return salt

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
            l1 = self.get_hash_l1()
        l2 = hashlib.sha512((l1 + date).encode('utf8')).digest()
        return base64.urlsafe_b64encode(l2).decode('utf8')

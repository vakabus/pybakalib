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
import requests

import xmltodict as xmltodict
import auth


class BakaClient(object):
    def __init__(self, url):
        self.url = BakaClient._fix_url(url)
        self.token = None
        self.available_modules = set()
        self.cache = {}

    @staticmethod
    def _fix_url(url):
        if not url.startswith('http'):
            url = 'http://' + url
        url = url.replace('login.aspx', '')
        if not url.endswith('/'):
            url += '/'
        return url

    def get_resource(self, params):
        if self.token is not None:
            params['hx'] = self.token
        req = requests.get(self.url + 'login.aspx', params)
        req.encoding = 'utf8'
        return req.text

    def login(self, *args, **kargs):
        self.token = auth.get_token(self, *args, **kargs)
        if self.token is None:
            raise auth.LoginError('Invalid username')

        try:
            login_xml = self.get_resource({'pm': 'login'})
            root = ET.fromstring(login_xml)
            if root.find('result').text != '01':
                raise auth.LoginError('Invalid password.')
            self.available_modules = list(filter(lambda x: len(x) > 0, root.find('moduly').text.split('*')))
        except ET.ParseError as orig:
            raise ConnectionError('Response from server was invalid. Try again.') from orig

    def is_module_available(self, name):
        return name in self.available_modules

    def get_module_xml(self, module_name):
        if module_name in self.cache:
            return self.cache[module_name]
        if not self.is_module_available(module_name):
            raise NotImplementedError('Server does not support such an operation')

        module_xml = self.get_resource({'pm': module_name})
        self.cache[module_name] = module_xml
        return module_xml

    def get_module(self, module_name):
        return xmltodict.parse(
            self.get_module(module_name),
            encoding='utf8'
        )

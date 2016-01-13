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
import urllib.request
import urllib.parse

from . import auth


class BakaClient(object):
    def __init__(self, url):
        self.url = BakaClient._fix_url(url)
        self.token = None
        self.available_modules = {}

    @staticmethod
    def _fix_url(url):
        if not url.startswith('http'):
            url = 'http://' + url
        url = url.replace('login.aspx','')
        if not url.endswith('/'):
            url = url + '/'
        return url

    def get_resource(self, params):
        if not self.token is None:
            params['hx'] = self.token
        url = self.url + 'login.aspx?' + urllib.parse.urlencode(params)
        with urllib.request.urlopen(url) as req:
            return req.read().decode('utf8')

    def login(self, *args, **kargs):
        self.token = auth.get_token(self, *args, **kargs)
        if self.token is None:
            raise auth.LoginError('Invalid username')

        try:
            login_xml = self.get_resource({'pm':'login'})
            root = ET.fromstring(login_xml)
            if root.find('result').text != '01':
                raise auth.LoginError('Invalid password.')
            self.available_modules = list(filter(lambda x: len(x) > 0,root.find('moduly').text.split('*')))
        except ParseError as orig:
            raise ConnectionError('Response from server was invalid. Try again.') from orig

    def is_module_available(self, name):
        return name in self.available_modules

    def get_module_xml(self, module_name):
        if not self.is_module_available(module_name):
            raise NotImplementedError('Server does not support such an operation')

        module_xml = self.get_resource({'pm': module_name})
        return module_xml

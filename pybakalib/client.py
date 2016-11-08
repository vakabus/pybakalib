#! /usr/bin/env python3

"""
This file is part of Pybakalib.

Pybakalib is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Pybakalib is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Pybakalib.  If not, see <http://www.gnu.org/licenses/>.
"""

import requests
import xmltodict as xmltodict
from xml.parsers.expat import ExpatError
from requests import RequestException

from pybakalib import auth
from pybakalib.errors import BakalariError, LoginError, BakalariParseError
from pybakalib.modules import MODULES

MAX_RETRIES = 5


class BakaClient(object):
    def __init__(self, url):
        self.url = BakaClient._fix_url(url)
        self.token_perm = None
        self.token = None
        self.__available_modules = set()
        self.__xml_cache = {}

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

        for i in range(MAX_RETRIES):
            try:
                req = requests.get(self.url + 'login.aspx', params=params)
                if req.status_code == 200:
                    req.encoding = 'utf8'
                    return req.text
            except RequestException:
                pass
        raise BakalariError('Could not contact server successfully')

    def login(self, *args, **kargs):
        tkns = auth.get_token(self, *args, **kargs)
        if tkns is None:
            raise LoginError('Invalid username')
        self.token_perm = tkns[0]
        self.token = tkns[1]

        try:
            profile = self.get_module('login')
            self.__available_modules = set(profile.available_modules)
        except BakalariError as orig:
            raise LoginError('Invalid password.') from orig

    def is_module_available(self, name):
        return name == 'login' or name in self.__available_modules

    def get_module_xml(self, module_name):
        if module_name in self.__xml_cache:
            return self.__xml_cache[module_name]
        if not self.is_module_available(module_name):
            raise NotImplementedError('Server does not support module ' + module_name.upper())

        module_xml = self.get_resource({'pm': module_name})
        self.__xml_cache[module_name] = module_xml
        return module_xml

    def get_module(self, module_name, retry=0):
        xml = self.get_module_xml(module_name)
        try:
            return MODULES[module_name](
                xmltodict.parse(
                    xml,
                    encoding='cp1250'
                )
            )
        except (ExpatError, AttributeError) as e:
            if retry > 3:
                raise BakalariParseError("Failed to parse module {}:\n\n{}".format(module_name, xml)) from e
            else:
                del self.__xml_cache[module_name]
                return self.get_module(module_name, retry=retry+1)

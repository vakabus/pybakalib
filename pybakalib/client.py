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
from typing import Optional

import requests
import xmltodict as xmltodict
from xml.parsers.expat import ExpatError
from requests import RequestException

from pybakalib import auth
from pybakalib.errors import BakalariError, LoginError, BakalariParseError, BakalariModuleNotImplementedError
from pybakalib.modules import MODULES

MAX_RETRIES = 5


class ResponseCache(object):
    def __init__(self):
        self.__cache = {}
        self.__cache.setdefault(None)

    def store(self, url: str, token: str, module: str, data: str):
        self.__cache["{}{}{}".format(url,token,module)] = data

    def get(self, url: str, token: str, module: str) -> Optional[str]:
        return self.__cache.get("{}{}{}".format(url, token, module))


class BakaClient(object):
    def __init__(self, url, cache=ResponseCache()):
        self.url = BakaClient._fix_url(url)
        self.token_perm = None
        self.token = None
        self.__available_modules = set()
        self.__module_cache = cache

    @staticmethod
    def _fix_url(url):
        if not url.startswith('http'):
            url = 'http://' + url
        url = url.replace('login.aspx', '')
        if not url.endswith('/'):
            url += '/'
        return url

    def get_resource(self, params) -> str:
        if self.token is not None:
            params['hx'] = self.token

        for i in range(MAX_RETRIES):
            try:
                req = requests.get(self.url + 'login.aspx', params=params, timeout=10)
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
        if not self.is_module_available(module_name):
            raise BakalariModuleNotImplementedError('Server does not support module ' + module_name.upper())

        module_xml = self.get_resource({'pm': module_name})

        return module_xml

    def get_module(self, module_name, retry=0):
        # Obtain module XML
        xml = self.__module_cache.get(self.url, self.token_perm, module_name)
        if xml is None:
            xml = self.get_module_xml(module_name)

        # Parse module XML
        try:
            if 'DOCTYPE HTML' in xml:
                raise BakalariParseError('Server responded with HTML instead of XML...')
            result = MODULES[module_name](
                xmltodict.parse(
                    xml,
                    #encoding='cp1250'          # I don't remember, why did I put it here. Now it looks like nonsense
                )
            )
            self.__module_cache.store(self.url, self.token_perm, module_name, xml)
            return result
        except (BakalariError, ExpatError, AttributeError) as e:
            if retry > 3:
                i = len(xml) if len(xml) < 80 else 80  # append first 80 characters to the error msg
                raise BakalariParseError("Failed to parse module {}:\n\n{}".format(module_name, xml[:i])) from e
            else:
                return self.get_module(module_name, retry=retry+1)

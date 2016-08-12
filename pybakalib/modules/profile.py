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
from pybakalib.errors import BakalariError


class Profile(object):
    def __init__(self, module_login):
        if module_login['results']['result'] != '01':
            raise BakalariError('Server error')
        self.name = module_login['results']['jmeno']
        self.school = module_login['results']['skola']
        self.available_modules = [x for x in module_login['results']['moduly'].split('*') if x != '']



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

from ..client import BakaClient as Client
import getpass

print('This is an example how you could use this library. Please log in.')
url      = input('URL: ')
username = input('Username: ')
password = getpass.getpass('Password: ')

client = Client(url)
client.login(username, password)
marks = client.get_module('znamky')
weights = client.get_module('predvidac')

for subj, aver in marks.get_all_averages(weights):
    print(subj, round(aver, 2))


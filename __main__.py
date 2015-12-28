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

from . import bakalari

print('This is an example how you could use this library. Please log in.')
url      = input('URL: ')
username = input('Username: ')
password = input('Password: ')

b = bakalari.BakaAccount(url,username=username,password=password)

#print('\nXML marks data')
#print(b.get_module_xml('znamky'))

print('\nWeighted averages of marks')
marks = b.get_marks()

averages = [ (subj.abbreviation, round(subj.get_weighted_average(),2)) for subj in marks.subjects]
averages.sort(key=lambda x: x[1])
for abbr, aver in averages:
    print(abbr + '\t' + str(aver))

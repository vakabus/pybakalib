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
from datetime import datetime


class MarksModule(object):
    def __init__(self, client):
        xml_marks = client.get_module_xml('znamky')
        xml_mark_weights = client.get_module_xml('predvidac')

        self.weights = MarksModule._parse_mark_weights(xml_mark_weights)
        self.subjects = MarksModule._parse_subjects(xml_marks)

    def get_subject(self, name):
        for subj in self.subjects:
            if subj.name == name:
                return subj
        return None

    @staticmethod
    def _parse_subjects(xml_marks):
        root = ET.fromstring(xml_marks)
        subjects = []
        for subject in root.find('predmety').findall('predmet'):
            subjects.append(Subject(subject))
        return subjects

    @staticmethod
    def _parse_mark_weights(xml_mark_types):
        root = ET.fromstring(xml_mark_types)
        weights = {}
        for typ in root.find('typypru').findall('typ'):
            weights[typ.find('nazev').text] = int(typ.find('vaha').text)
        return weights


class Subject(object):
    def __init__(self, xml_root):
        self.marks = []
        self.name = xml_root.find('nazev').text
        self.abbreviation = xml_root.find('zkratka').text

        for mark in xml_root.find('znamky').findall('znamka'):
            self.marks.append(Mark(mark))
        self.marks.sort(key=lambda x: x.date)

    def add_mark(self, mark):
        self.marks.append(mark)

    def get_marks(self):
        return self.marks

    def get_weighted_average(self, weights, up_to=-1):
        """
        Returns weighted average of marks. If there are no marks, returns -1.
        """
        up_to = len(self.marks) if up_to == -1 else up_to

        w_sum = sum([s.get_weight(weights) for s in self.marks[:up_to]])
        a_sum = sum([s.get_weight(weights) * float(s) for s in self.marks[:up_to]])

        if w_sum == 0:
            return -1
        else:
            return a_sum / w_sum


class Mark(object):
    def __init__(self, xml_mark, mark=1, label='pololetní práce'):
        if xml_mark is None:
            self.mark = mark
            self.label = label
        else:
            self.mark = xml_mark.find('znamka').text
            self.caption = xml_mark.find('caption').text
            self.description = xml_mark.find('poznamka').text
            self.label = xml_mark.find('ozn').text
            self.date = datetime.strptime(xml_mark.find('udeleno').text, "%y%m%d%H%M")

    def __float__(self):
        try:
            return float(self.mark.replace('-', '.5'))
        except:
            return 0.0

    def get_weight(self, weights):
        if float(self) == 0:
            return 0
        return weights[self.label]

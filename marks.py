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
    @staticmethod
    def parse_marks(root, mark_types):
        subjects = []
        for subject in root.find('predmety').findall('predmet'):
            subjects.append(Subject.parse_subject_xml(subject, mark_types))
        return subjects
    def __init__(self, xml_marks, xml_mark_types):
        self.types = MarkTypes(xml_mark_types)
        self.subjects = MarksModule.parse_marks(ET.fromstring(xml_marks),
                                                self.types)
    def get(self, name):
        for subj in self.subjects:
            if subj.name == name:
                return subj
        return None


"""
MarkTypes instances holds weight values for different types of marks.
"""
class MarkTypes(object):
    @staticmethod
    def parse_xml(root):
        weights = {}
        for typ in root.find('typypru').findall('typ'):
            weights[typ.find('nazev').text] = int(typ.find('vaha').text)
        return weights

    def __init__(self, xml_mark_types):
        self.marks = MarkTypes.parse_xml(ET.fromstring(xml_mark_types))

    def get_weight(self, m_type):
        return self.marks[m_type]

class Subject(object):
    @staticmethod
    def parse_subject_xml(subject, mark_types):
        name = subject.find('nazev').text
        abbrev = subject.find('zkratka').text
        subj = Subject(name, abbreviation=abbrev)
        for mark in subject.find('znamky').findall('znamka'):
            subj.add_mark(Mark.parse_mark_xml(mark, mark_types))
        subj.marks.sort(key=lambda x: x.date)
        return subj
    def __init__(self, name, abbreviation=None):
        self.marks = []
        self.name = name
        self.abbreviation = abbreviation
    def add_mark(self, mark):
        self.marks.append(mark)
    def get_marks(self):
        return self.marks
    """
    Returns weighted average of marks. If there are no marks, returns -1.
    """
    def get_weighted_average(self, up_to=-1):
        up_to = len(self.marks) if up_to == -1 else up_to

        w_sum = sum([s.weight for s in self.marks[:up_to]])
        a_sum = sum([s.weight * s.mark_float() for s in self.marks[:up_to]])

        if w_sum == 0:
            return -1
        else:
            return a_sum / w_sum

class Mark(object):
    @staticmethod
    def parse_mark_xml(mark, mark_types):
        description = mark.find('poznamka').text
        caption = mark.find('caption').text
        weight = mark_types.get_weight(mark.find('ozn').text)
        mark_s = mark.find('znamka').text
        date = datetime.strptime(mark.find('udeleno').text, "%y%m%d%H%M")
        return Mark(description, caption, weight, mark_s, date)
    def __init__(self, description, caption, weight, mark, date):
        self.mark = mark
        self.caption = caption
        self.description = description
        self.weight = weight
        self.date = date
    def mark_float(self):
        try:
            return float(self.mark.replace('-', '.5'))
        except:
            return 0

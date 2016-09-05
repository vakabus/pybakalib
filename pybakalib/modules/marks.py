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

from datetime import datetime


class MarksModule(list):
    def __init__(self, module_marks):
        super(MarksModule, self).__init__()
        if module_marks['results']['predmety'] is None:
            return
        for subj in module_marks['results']['predmety']['predmet']:
            self.append(Subject(subj))

    def get_subject(self, name):
        for subj in self:
            if subj.name == name:
                return subj
        return None

    def list_subject_names(self):
        return [subj.name for subj in self]

    def get_all_averages(self, weights):
        averages = []
        for subj in self:
            averages.append((subj.name, subj.get_weighted_average(weights)))
        averages.sort(key=lambda x: x[1] if x[1] is not None else float('-inf'), reverse=True)
        return averages


class Subject(object):
    def __init__(self, dict_subject):
        self.marks = []                                 # type: List[Mark]
        self.name = dict_subject['nazev']               # type: str
        self.abbreviation = dict_subject['zkratka']     # type: str

        if 'znamky' in dict_subject and dict_subject['znamky'] is not None:     # check for empty subjects
            for mark in dict_subject['znamky']['znamka']:
                self.add_mark(Mark(mark))
            self.marks.sort(key=lambda x: x.date)

    def add_mark(self, mark):
        self.marks.append(mark)

    def get_marks(self):
        return self.marks

    def get_weighted_average(self, weights, up_to=-1):
        """
        Returns weighted average of marks. If there are no marks, returns -1.
        :keyword up_to Optional number of marks from beginning, for which to calculate average.
        """
        up_to = len(self.marks) if up_to == -1 else up_to

        w_sum = sum([s.get_weight(weights) for s in self.marks[:up_to]])
        a_sum = sum([s.get_weight(weights) * float(s) for s in self.marks[:up_to]])

        if w_sum == 0:
            return None
        else:
            return round(a_sum / w_sum, 2)


class Mark(object):
    def __init__(self, dict_mark, mark=1, label='pololetní práce'):
        self.mark = mark                    # type: str
        self.label = label                  # type: str
        self.date = None                    # type: datetime
        self.description = None             # type: str
        self.caption = None                 # type: str

        if dict_mark is not None:
            self.mark = dict_mark['znamka']
            self.caption = dict_mark['caption']
            self.description = dict_mark['poznamka']
            self.label = dict_mark['ozn']
            self.date = datetime.strptime(dict_mark['udeleno'], "%y%m%d%H%M")

    def __float__(self):
        try:
            return float(self.mark.replace('-', '.5'))
        except:
            return 0.0

    def get_weight(self, weights):
        if float(self) == 0:
            return 0
        return weights[self.label]

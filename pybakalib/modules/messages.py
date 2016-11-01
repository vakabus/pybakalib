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


class ReceivedMessages(list):
    def __init__(self, module_messages):
        super(ReceivedMessages, self).__init__()
        if module_messages['results']['zpravy'] is None:
            return
        z = module_messages['results']['zpravy']['zprava']
        board = z if isinstance(z, list) else [z]
        for mess in board:
            self.append(Message(mess))
        self.sort(key=lambda x: x.date, reverse=True)


class Message(object):
    def __init__(self, message):
        self.sender = message['od']
        self.title = message['nadpis']
        self.text = message['text']
        self.date = datetime.strptime(message['cas'], "%y%m%d%H%M")
        self.id = message['id']
        self.has_attachment = message['files'] != '0'

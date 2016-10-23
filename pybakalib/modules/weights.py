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


def parse_weights(module_weights) -> dict:
    weights = {}
    w = module_weights['results']['typypru']['typ']
    wl = w if isinstance(w, list) else [w]      # fixes when there is only one weight and it does not return a list
    for typ in wl:
        weights[typ['nazev']] = int(typ['vaha'])
    return weights
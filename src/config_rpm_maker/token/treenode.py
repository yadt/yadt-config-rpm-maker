#   yadt-config-rpm-maker
#   Copyright (C) 2011-2013 Immobilien Scout GmbH
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Created on Aug 12, 2011

@author: Michael Gruber, Konrad Hosemann
"""


class NameNotAcceptedException(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "name '%s' is not accepted, must not be empty or null" % self.name


class TreeNode:
    def __init__(self, name, children=[]):
        if name is None or len(name) == 0:
            raise NameNotAcceptedException(name)
        self.name = name
        self.children = set(children)

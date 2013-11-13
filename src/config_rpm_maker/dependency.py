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

import re

from types import ListType


class Dependency:
    """Consumes raw formatted RPM dependencies. Eighter accumulates them or collapses them so the first/gerneral
    ones get overwritten by the later/specific ones"""

    def __init__(self, collapseDependencies=False, filterRegex=".*", positiveFilter=True):
        self.dependencies = dict([])
        self.collapseDependencies = collapseDependencies
        self.filterRegex = filterRegex
        self.positiveFilter = positiveFilter

    def __filterDeps(self):
        filteredDependencies = dict([])
        for package, dependency in self.dependencies.items():
            if re.match(self.filterRegex, package):
                if self.positiveFilter:
                    filteredDependencies[package] = dependency
            else:
                if not self.positiveFilter:
                    filteredDependencies[package] = dependency
        self.dependencies = filteredDependencies

    def __add(self, rawDependencyString):
        dependency = re.sub("\s*([<>=]+)\s*", "\\1", rawDependencyString)  # remove spaces around <>=
        dependency = re.sub("\s*,\s*", "\n", dependency)         # change , spearator into newline
        dependency = re.sub("\s+", "\n", dependency)             # all spaces left are separators now, change into newline
        dependency = re.sub("([<>=]+)", " \\1", dependency)      # add a space in front of <>= so we have tuples now

        for dependency in dependency.split("\n"):
            if len(dependency.strip()) != 0:
                if re.search(" ", dependency):
                    (package, versionSpec) = dependency.split(" ")
                    dependency = re.sub("\s*([<>=]+\s*)", " \\1 ", dependency)  # add a surrounding space
                else:
                    package = dependency

                if (package in self.dependencies) and not self.collapseDependencies:
                    if self.dependencies[package] != dependency:
                        self.dependencies[package] = self.dependencies[package] + ", " + dependency
                else:
                    self.dependencies[package] = dependency

    def add(self, rawDependencies):
        if isinstance(rawDependencies, ListType):
            for item in rawDependencies:
                self.__add(item)
        else:
            self.__add(rawDependencies)
        self.__filterDeps()

    def __repr__(self):
        """nicely prints the previously <code>add()</code>ed RPM dependencies"""
        return ", ".join(self.dependencies.values())

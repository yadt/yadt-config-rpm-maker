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
    """ Consumes raw formatted RPM dependencies. Either accumulates them or overwrites them
        so the first/gerneral ones get overwritten by the later/specific ones """

    def __init__(self, accumulate_dependencies=True, filter_regex=".*", positive_filter=True):
        self.dependencies = dict([])
        self.accumulate_dependencies = accumulate_dependencies
        self.filter_regex = filter_regex
        self.positive_filter = positive_filter

    def _filter_dependencies(self):
        filtered_dependencies = dict([])
        for package, dependency in self.dependencies.items():
            if re.match(self.filter_regex, package):
                if self.positive_filter:
                    filtered_dependencies[package] = dependency
            else:
                if not self.positive_filter:
                    filtered_dependencies[package] = dependency
        self.dependencies = filtered_dependencies

    def _add(self, raw_dependency_string):
        dependency = re.sub("\s*([<>=]+)\s*", "\\1", raw_dependency_string)  # remove spaces around <>=
        dependency = re.sub("\s*,\s*", "\n", dependency)         # change ',' separator into newline
        dependency = re.sub("\s+", "\n", dependency)             # all spaces left are separators now, change into newline
        dependency = re.sub("([<>=]+)", " \\1", dependency)      # add a space in front of <>= so we have tuples now

        for dependency in dependency.split("\n"):
            dependency = dependency.strip()
            if dependency:
                if " " in dependency:
                    (package, versionSpec) = dependency.split(" ")
                    dependency = re.sub("\s*([<>=]+\s*)", " \\1 ", dependency)  # add a surrounding space
                else:
                    package = dependency

                if (package in self.dependencies) and self.accumulate_dependencies:
                    if self.dependencies[package] != dependency:
                        self.dependencies[package] = self.dependencies[package] + ", " + dependency
                else:
                    self.dependencies[package] = dependency

    def add(self, raw_dependencies):
        if isinstance(raw_dependencies, ListType):
            for item in raw_dependencies:
                self._add(item)
        else:
            self._add(raw_dependencies)
        self._filter_dependencies()

    def __str__(self):
        """ nicely prints the previously added RPM dependencies """

        return ", ".join(self.dependencies.values())

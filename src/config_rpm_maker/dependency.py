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
        # Looks like    {'httpd': set(['httpd', 'httpd = 42'])}
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
        dependencies = re.sub("\s*([<>=]+)\s*", "\\1", raw_dependency_string)  # remove spaces around <>=
        dependencies = re.sub("\s*,\s*", "\n", dependencies)         # change ',' separator into newline
        dependencies = re.sub("\s+", "\n", dependencies)             # all spaces left are separators now, change into newline
        dependencies = re.sub("([<>=]+)", " \\1 ", dependencies)     # add spaces around <>=

        for new_dependency in dependencies.split("\n"):
            new_dependency = new_dependency.strip()
            if new_dependency:
                package = new_dependency.split(" ", 1)[0]

                if (package in self.dependencies) and self.accumulate_dependencies:
                    self.dependencies[package].add(new_dependency)
                else:
                    self.dependencies[package] = set([new_dependency])

    def add(self, raw_dependencies):
        if isinstance(raw_dependencies, ListType):
            for item in raw_dependencies:
                self._add(item)
        else:
            self._add(raw_dependencies)
        self._filter_dependencies()

    def __str__(self):
        """return RPM dependencies formatted for use in the spec file"""
        return ", ".join(", ".join(deps) for deps in self.dependencies.values())

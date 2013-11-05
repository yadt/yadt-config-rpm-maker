__author__ = "Ingmar Krusch"
__email__ = "krusch@immobilienscout24.de"
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

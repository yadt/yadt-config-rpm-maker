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

from unittest import TestCase

from config_rpm_maker.dependency import Dependency


class DependencyTest(TestCase):

    def setUp(self):
        self.identicalDependAsString = "a=1, b >2, a> 3 c = 4 a< 5"
        self.identicaldependAsList = ["a=1", "b >2", "a> 3", "c = 4", "a< 5"]
        self.identicaldependAsStringWiredlyFormatted = """
                a
                =1, b >
                2, a> 3                  c = 4


                        a<                   5

                        """

    def test_should_filter_for_repos(self):
        rawDependency = "yadt-foo yadt-dev-snapshots-repo yadt-bla yadt-boo-repo"
        dep = Dependency(accumulate_dependencies=False, filter_regex="^yadt-.*-repo$")
        dep.add(rawDependency)
        result = str(dep)
        self.assertEqual(result.count("yadt-dev-snapshots-repo"), 1, msg="Don't have yadt-dev-snaphosts-repo in <" + result + ">")
        self.assertEqual(result.count("yadt-boo-repo"), 1, msg="Don't have yadt-boo-repo in <" + result + ">")
        self.assertEqual(result.count("yadt-foo"), 0, msg="Filter don't work. Found yadt-foo <" + result + ">")
        self.assertEqual(result.count("yadt-bla"), 0, msg="Filter don't work. Found yadt-bla <" + result + ">")

    def test_should_negative_filter_for_repos(self):
        rawDependency = "yadt-foo yadt-dev-snapshots-repo yadt-bla yadt-boo-repo"
        dep = Dependency(accumulate_dependencies=False, filter_regex="^yadt-.*-repo$", positive_filter=False)
        dep.add(rawDependency)
        result = str(dep)
        self.assertEqual(result.count("yadt-dev-snapshots-repo"), 0, msg="Filter don't work. Found yadt-dev-snaphosts-repo in <" + result + ">")
        self.assertEqual(result.count("yadt-boo-repo"), 0, msg="Filter don't work. Found yadt-boo-repo in <" + result + ">")
        self.assertEqual(result.count("yadt-foo"), 1, msg="Filter don't work. Not found yadt-foo <" + result + ">")
        self.assertEqual(result.count("yadt-bla"), 1, msg="Filter don't work. Not found yadt-bla <" + result + ">")

    def test_should_multiple_completly_equal_dependencies_get_always_overwritten(self):
        rawDependency = "httpd httpd httpd a b httpd"
        dep = Dependency(accumulate_dependencies=True)
        dep.add(rawDependency)
        result = str(dep)
        self.assertEqual(result.count("a"), 1, msg="Don't have the right amount of 'a' <" + result + ">")
        self.assertEqual(result.count("b"), 1, msg="Don't have the right amount of 'b' <" + result + ">")
        self.assertEqual(result.count("httpd"), 1, msg="Don't have the right amount of 'httpd' <" + result + ">")

    def test_should_remove_duplicates(self):
        rawDependency = "httpd httpd>42 httpd"
        dep = Dependency(accumulate_dependencies=True)
        dep.add(rawDependency)
        result = str(dep)
        # Duplicate "httpd" must have been removed. Since set() is used to remove
        # duplices, we cannot rely on the exact order.
        one = "httpd, httpd > 42"
        two = "httpd > 42, httpd"
        self.assertTrue(result in (one, two))

    def test_should_multiple_completly_equal_dependencies_get_always_overwritten_but_differing_version_spec_count_as_not_equal(self):
        rawDependency = "httpd httpd httpd a b httpd a httpd > 4"
        dep = Dependency(accumulate_dependencies=True)
        dep.add(rawDependency)
        result = str(dep)
        self.assertEqual(result.count("a"), 1, msg="Don't have the right amount of 'a' <" + result + ">")
        self.assertEqual(result.count("b"), 1, msg="Don't have the right amount of 'b' <" + result + ">")
        self.assertEqual(result.count("httpd"), 2, msg="Don't have the right amount of 'httpd' <" + result + ">")

    def test_should_read_dependency_with_snapshot_as_version_mixed_with_digits_only_overwrite(self):
        rawDependency = "a= 12 dummy-snapshot = 1.30-SNAPSHOT20100819155634 a = 13"
        dep = Dependency(accumulate_dependencies=False)
        dep.add(rawDependency)
        result = str(dep)
        self.assertEquals("a = 13, dummy-snapshot = 1.30-SNAPSHOT20100819155634", result)

    def test_should_read_dependency_with_snapshot_as_version(self):
        rawDependency = """dummy-snapshot = 1.30-SNAPSHOT20100819155634"""
        dep = Dependency(accumulate_dependencies=False)
        dep.add(rawDependency)
        result = str(dep)
        self.assertEqual("dummy-snapshot = 1.30-SNAPSHOT20100819155634", result)

    def test_should_read_dependencies_from_args_not_overwritten_and_list(self):
        resultString = self.__readDependencies(self.identicalDependAsString, True)
        resultList = self.__readDependencies(self.identicaldependAsList, True)
        self.assertEqual(resultString, resultList)

    def test_should_read_dependencies_overwritten_from_args_and_list(self):
        resultString = self.__readDependencies(self.identicalDependAsString, False)
        resultList = self.__readDependencies(self.identicaldependAsList, False)
        self.assertEqual(resultString, resultList)

    def test_should_read_dependencies_not_overwritten_from_args(self):
        resultString = self.__readDependencies(self.identicalDependAsString, True)
        self.__checkDependenciesAreCorrectAndNotCollapsed(resultString)

    def test_should_read_dependencies_overwritten_from_args(self):
        resultString = self.__readDependencies(self.identicalDependAsString, False)
        self.__checkDependenciesAreCorrectAndCollapsed(resultString)

    def test_should_read_dependencies_overwritten_from_wired_args(self):
        resultWired = self.__readDependencies(self.identicaldependAsStringWiredlyFormatted, False) # todo f***ing typo
        self.__checkDependenciesAreCorrectAndCollapsed(resultWired)

    def test_should_read_dependencies_not_overwritten_from_wired_args(self):
        resultWired = self.__readDependencies(self.identicaldependAsStringWiredlyFormatted, True)
        self.__checkDependenciesAreCorrectAndNotCollapsed(resultWired)

    def __readDependencies(self, rawDependencies, overwriteDuplicates):
        dep = Dependency(accumulate_dependencies=overwriteDuplicates)
        dep.add(rawDependencies)
        return str(dep)

    def __checkDependenciesAreCorrectAndNotCollapsed(self, result):
        # check that all keys are present multiple times
        self.assertEqual(result.count("a"), 3)
        self.assertEqual(result.count("b"), 1)
        self.assertEqual(result.count("c"), 1)
        # check that each given versionSpec is present
        self.assertEqual(result.count("1"), 1)
        self.assertEqual(result.count("2"), 1)
        self.assertEqual(result.count("3"), 1)
        self.assertEqual(result.count("4"), 1)
        self.assertEqual(result.count("5"), 1)

    def __checkDependenciesAreCorrectAndCollapsed(self, result):
        # check that all keys are present only once
        self.assertEqual(result.count("a"), 1)
        self.assertEqual(result.count("b"), 1)
        self.assertEqual(result.count("c"), 1)
        # check that only the latest versionSpec is present
        self.assertEqual(result.count("1"), 0)
        self.assertEqual(result.count("2"), 1)
        self.assertEqual(result.count("3"), 0)
        self.assertEqual(result.count("4"), 1)
        self.assertEqual(result.count("5"), 1)

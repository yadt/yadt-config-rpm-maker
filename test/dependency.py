__author__ = "Ingmar Krusch"
__email__ = "krusch@immobilienscout24.de"


from config_rpm_maker.dependency import Dependency
from unittest import TestCase

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

    def test_filter_for_repos(self):
        rawDependency = "yadt-foo yadt-dev-snapshots-repo yadt-bla yadt-boo-repo"
        dep = Dependency(False, "^yadt-.*-repo$")
        dep.add(rawDependency)
        result = repr(dep)
        self.assertEqual(result.count("yadt-dev-snapshots-repo"), 1, msg="Don't have yadt-dev-snaphosts-repo in <" + result + ">")
        self.assertEqual(result.count("yadt-boo-repo"), 1, msg="Don't have yadt-boo-repo in <" + result + ">")
        self.assertEqual(result.count("yadt-foo"), 0, msg="Filter don't work. Found yadt-foo <" + result + ">")
        self.assertEqual(result.count("yadt-bla"), 0, msg="Filter don't work. Found yadt-bla <" + result + ">")

    def test_negative_filter_for_repos(self):
        rawDependency = "yadt-foo yadt-dev-snapshots-repo yadt-bla yadt-boo-repo"
        dep = Dependency(False, "^yadt-.*-repo$", False)
        dep.add(rawDependency)
        result = repr(dep)
        self.assertEqual(result.count("yadt-dev-snapshots-repo"), 0, msg="Filter don't work. Found yadt-dev-snaphosts-repo in <" + result + ">")
        self.assertEqual(result.count("yadt-boo-repo"), 0, msg="Filter don't work. Found yadt-boo-repo in <" + result + ">")
        self.assertEqual(result.count("yadt-foo"), 1, msg="Filter don't work. Not found yadt-foo <" + result + ">")
        self.assertEqual(result.count("yadt-bla"), 1, msg="Filter don't work. Not found yadt-bla <" + result + ">")

    def test_multipleCompletlyEqualDependenciesGetAlwaysCollapsed(self):
        rawDependency = "httpd httpd httpd a b httpd"
        dep = Dependency(False)
        dep.add(rawDependency)
        result = repr(dep)
        self.assertEqual(result.count("a"), 1, msg="Don't have the right amount of 'a' <" + result + ">")
        self.assertEqual(result.count("b"), 1, msg="Don't have the right amount of 'b' <" + result + ">")
        self.assertEqual(result.count("httpd"), 1, msg="Don't have the right amount of 'httpd' <" + result + ">")

    def test_multipleCompletlyEqualDependenciesGetAlwaysCollapsedButDifferingVersionSpecCountAsNotEqual(self):
        rawDependency = "httpd httpd httpd a b httpd a httpd > 4"
        dep = Dependency(False)
        dep.add(rawDependency)
        result = repr(dep)
        self.assertEqual(result.count("a"), 1, msg="Don't have the right amount of 'a' <" + result + ">")
        self.assertEqual(result.count("b"), 1, msg="Don't have the right amount of 'b' <" + result + ">")
        self.assertEqual(result.count("httpd"), 2, msg="Don't have the right amount of 'httpd' <" + result + ">")

    def test_readDependencyWithSnapshotAsVersionMixedWithDigitsOnlyCollapse(self):
        rawDependency = "a= 12 dummy-snapshot = 1.30-SNAPSHOT20100819155634 a = 13"
        dep = Dependency(True)
        dep.add(rawDependency)
        result = repr(dep)
        self.assertEquals("a = 13, dummy-snapshot = 1.30-SNAPSHOT20100819155634", result)

    def test_readDependencyWithSnapshotAsVersion(self):
        rawDependency = """dummy-snapshot = 1.30-SNAPSHOT20100819155634"""
        dep = Dependency(True)
        dep.add(rawDependency)
        result = repr(dep)
        self.assertEqual("dummy-snapshot = 1.30-SNAPSHOT20100819155634", result)

    def test_readDependenciesFromArgsNotCollapsedAndList(self):
        resultString = self.__readDependencies(self.identicalDependAsString, False)
        resultList = self.__readDependencies(self.identicaldependAsList, False)
        self.assertEqual(resultString, resultList)

    def test_readDependenciesCollapsedFromArgsAndList(self):
        resultString = self.__readDependencies(self.identicalDependAsString, True)
        resultList = self.__readDependencies(self.identicaldependAsList, True)
        self.assertEqual(resultString, resultList)

    def test_readDependenciesNotCollapsedFromArgs(self):
        resultString = self.__readDependencies(self.identicalDependAsString, False)
        self.__checkDependenciesAreCorrectAndNotCollapsed(resultString)

    def test_readDependenciesCollapsedFromArgs(self):
        resultString = self.__readDependencies(self.identicalDependAsString, True)
        self.__checkDependenciesAreCorrectAndCollapsed(resultString)

    def test_readDependenciesCollapsedFromWiredArgs(self):
        resultWired = self.__readDependencies(self.identicaldependAsStringWiredlyFormatted, True)
        self.__checkDependenciesAreCorrectAndCollapsed(resultWired)

    def test_readDependenciesNotCollapsedFromWiredArgs(self):
        resultWired = self.__readDependencies(self.identicaldependAsStringWiredlyFormatted, False)
        self.__checkDependenciesAreCorrectAndNotCollapsed(resultWired)

    def __readDependencies(self, rawDependencies, collapseDuplicates):
        dep = Dependency(collapseDuplicates)
        dep.add(rawDependencies)
        return repr(dep)

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

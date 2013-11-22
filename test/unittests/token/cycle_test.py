# coding=utf-8
#
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

import unittest

from config_rpm_maker.token.cycle import ContainsCyclesException
from config_rpm_maker.token.cycle import TokenCycleChecking


class CycleTest(unittest.TestCase):

    def test_should_recognize_simple_cycle(self):
        graph_with_cycle = {'foo': ['bar'],
                            'bar': ['foo']}

        actual_graph = TokenCycleChecking(graph_with_cycle)

        self.assertRaises(ContainsCyclesException, actual_graph.assert_no_cycles_present)

    def test_should_not_raise_exception_if_graph_empty(self):
        empty_graph = {}

        actual_graph = TokenCycleChecking(empty_graph)

        actual_graph.assert_no_cycles_present()

    def test_should_not_raise_exception_if_no_cycles_present(self):
        graph_with_no_cycles = {'foo': ['bar'],
                                'a': ['b'],
                                'baz': ['bar'],
                                'hello': ['foo']}

        actual_graph = TokenCycleChecking(graph_with_no_cycles)

        actual_graph.assert_no_cycles_present()

    def test_should_recognize_complex_cycle(self):
        graph_with_cycle = {'foo': ['bar'],
                            'bar': ['baz'],
                            'baz': ['abc'],
                            'abc': ['foo'],
                            'f': ['g'],
                            'j': ['k']}

        actual_graph = TokenCycleChecking(graph_with_cycle)

        self.assertRaises(ContainsCyclesException, actual_graph.assert_no_cycles_present)

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

    def test_recognizes_simple_cycle(self):
        graph_with_cycle = {}
        graph_with_cycle['foo'] = ['bar']
        graph_with_cycle['bar'] = ['foo']
        graphTest = TokenCycleChecking(graph_with_cycle)
        self.assertRaises(ContainsCyclesException, graphTest.assert_no_cycles_present)

    def test_does_not_fire_exception_if_graph_empty(self):
        empty_graph = {}
        graphTest = TokenCycleChecking(empty_graph)
        graphTest.assert_no_cycles_present()

    def test_does_not_fire_exception_if_no_cycles_present(self):
        graph_with_no_cycles = {}
        graph_with_no_cycles['foo'] = ['bar']
        graph_with_no_cycles['a'] = ['b']
        graph_with_no_cycles['baz'] = ['bar']
        graph_with_no_cycles['hello'] = ['foo']
        graphTest = TokenCycleChecking(graph_with_no_cycles)
        graphTest.assert_no_cycles_present()

    def test_recognizes_complex_cycle(self):
        graph_with_cycle = {}
        graph_with_cycle['foo'] = ['bar']
        graph_with_cycle['bar'] = ['baz']
        graph_with_cycle['baz'] = ['abc']
        graph_with_cycle['abc'] = ['foo']
        graph_with_cycle['f'] = ['g']
        graph_with_cycle['j'] = ['k']
        graphTest = TokenCycleChecking(graph_with_cycle)
        self.assertRaises(ContainsCyclesException, graphTest.assert_no_cycles_present)

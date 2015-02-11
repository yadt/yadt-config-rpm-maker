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

from logging import getLogger

from config_rpm_maker.utilities.logutils import verbose
from config_rpm_maker.exceptions import BaseConfigRpmMakerException

LOGGER = getLogger(__name__)


class ContainsCyclesException(BaseConfigRpmMakerException):
    error_info = "Variable cycle detected!"


class TokenCycleChecking(object):
    """
        Checks for cycles in a graph. The graph is represented using a dictionary.
        Examples: a graph with a cycle: {'foo': ['bar'],
                                         'bar': ['foo']}
                  a cycle free graph:   {'foo': ['bar'],
                                         'a': ['b'],
                                         'baz': ['bar'],
                                         'hello': ['foo']}
    """

    def __init__(self, edges):
        """ edges should be a dictionary defining the graph to check for cycles. """

        self.edges = edges

    def assert_no_cycles_present(self):

        verbose(LOGGER).debug('Checking that graph %s has no cycles.', self.edges)

        cycles = []
        components = tarjan_scc(self.edges)
        for component in components:
            if len(component) > 1:
                cycles.append(component)
                verbose(LOGGER).debug("Found cycle %s in graph %s", component, self.edges)
                # every nontrivial strongly connected component
                # contains at least one directed cycle, so len()>1 is a showstopper

        if len(cycles) > 0:
            error_message = "Found cycle(s) in variable declarations :\n"
            for cycle in cycles:
                error_message += "These variables form a cycle : " + str(cycle) + "\n"
            raise ContainsCyclesException(error_message)


def tarjan_scc(graph):
    """ Tarjan's partitioning algorithm for finding strongly connected components in a graph. """

    index_counter = [0]
    stack = []
    lowlinks = {}
    index = {}
    result = []

    def strongconnect(node):
        index[node] = index_counter[0]
        lowlinks[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)

        try:
            successors = graph[node]
        except Exception:
            successors = []
        for successor in successors:
            if successor not in lowlinks:
                strongconnect(successor)
                lowlinks[node] = min(lowlinks[node], lowlinks[successor])
            elif successor in stack:
                lowlinks[node] = min(lowlinks[node], index[successor])

        if lowlinks[node] == index[node]:
            connected_component = []

            while True:
                successor = stack.pop()
                connected_component.append(successor)
                if successor == node:
                    break
            component = tuple(connected_component)
            result.append(component)

    for node in graph:
        if node not in lowlinks:
            strongconnect(node)

    return result

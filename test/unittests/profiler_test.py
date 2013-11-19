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

from unittest import TestCase, main
from mock import patch

from config_rpm_maker.profiler import measure_execution_time


class ProfilerTests(TestCase):

    @patch('config_rpm_maker.profiler.LOGGER')
    def test_should_wrap_function(self, mock_LOGGER):

        self.dummy_function_has_been_executed = False

        def dummy_function():
            self.dummy_function_has_been_executed = True

        actual_function = measure_execution_time(dummy_function)
        actual_function()

        self.assertTrue(self.dummy_function_has_been_executed)

if __name__ == "__main__":
    main()

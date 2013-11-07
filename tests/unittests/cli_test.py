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
from mock import call, patch
from logging import INFO

from config_rpm_maker import initialize_logging


class CliTests(TestCase):

    @patch('config_rpm_maker.basicConfig')
    @patch('config_rpm_maker.config.get')
    def test_should_initialize_logging_using_configuration(self, mock_get, mock_basicConfig):
        def get_side_effect(key, default):
            return key
        mock_get.side_effect = get_side_effect

        initialize_logging()

        self.assertEqual(call(format="log_format", level="log_level"), mock_basicConfig.call_args)

    @patch('config_rpm_maker.basicConfig')
    @patch('config_rpm_maker.config.get')
    def test_should_use_default_values_when_getting_configuration_values(self, mock_get, mock_basicConfig):
        initialize_logging()

        self.assertEqual([call('log_format', '%(asctime)s %(levelname)5s [%(name)s] - %(message)s'),
                          call('log_level', INFO)],
                         mock_get.call_args_list)

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

from logging import DEBUG, ERROR, INFO
from mock import patch
from unittest import TestCase

from config_rpm_maker import config
from config_rpm_maker.config import DEFAULT_LOG_LEVEL, ConfigException, get_log_level, get_temporary_directory, setvalue


@patch("config_rpm_maker.config.get")
class GetTemporaryDirectoryTests(TestCase):

    def test_get_temporary_directory_should_use_key_for_temporary_directory(self, mock_get):
        get_temporary_directory()

        mock_get.assert_called_once_with('temp_dir')

    def test_get_temporary_directory_should_return_value_from_get(self, mock_get):
        mock_get.return_value = "temporary directory"

        actual = get_temporary_directory()

        self.assertEqual("temporary directory", actual)


@patch("config_rpm_maker.config.get")
class GetLogLevelTests(TestCase):

    def test_get_log_level_should_use_key_for_log_level(self, mock_get):
        mock_get.return_value = "DEBUG"

        get_log_level()

        mock_get.assert_called_once_with('log_level', DEFAULT_LOG_LEVEL)

    def test_get_log_level_should_return_debug_log_level(self, mock_get):
        mock_get.return_value = "DEBUG"

        actual = get_log_level()

        self.assertEqual(DEBUG, actual)

    def test_get_log_level_should_return_error_log_level(self, mock_get):
        mock_get.return_value = "ERROR"

        actual = get_log_level()

        self.assertEqual(ERROR, actual)

    def test_get_log_level_should_return_info_log_level(self, mock_get):
        mock_get.return_value = "INFO"

        actual = get_log_level()

        self.assertEqual(INFO, actual)

    def test_get_log_level_should_raise_exception_when_strange_log_level_given(self, mock_get):
        mock_get.return_value = "FOO"

        self.assertRaises(ConfigException, get_log_level)


class SetValueTests(TestCase):

    def test_should_raise_configuration_exception_when_trying_to_set_value_without_name(self):

        self.assertRaises(ConfigException, setvalue, name=None, value='123')

    @patch('config_rpm_maker.config.load_configuration_file')
    def test_should_load_configuration_if_no_configuration_properties_are_empty(self, mock_load_configuration_file):

        def set_configuration_properties():
            config.configuration = {}
        mock_load_configuration_file.side_effect = set_configuration_properties
        config.configuration = None

        setvalue('abc', '123')

        mock_load_configuration_file.assert_called_with()

    def test_should_set_value_of_configuration_properties(self):

        setvalue('abc', '123')

        self.assertEqual('123', config.configuration['abc'])

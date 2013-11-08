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

print "Imports of unittest, mock and logging"
from unittest import TestCase
from mock import patch
from logging import DEBUG, ERROR, INFO
print "Imports of unittest, mock and logging: ok"

print "Importing of config_rpm_maker.config"
from config_rpm_maker.config import DEFAULT_LOG_LEVEL, ConfigException, get_log_level, get_temporary_directory
print "Importing of config_rpm_maker.config: ok"


class ConfigurationTests(TestCase):

    @patch("config_rpm_maker.config.get")
    def test_get_temporary_directory_should_use_key_for_temporary_directory(self, mock_get):

        get_temporary_directory()

        mock_get.assert_called_once_with('temp_dir')

    @patch("config_rpm_maker.config.get")
    def test_get_temporary_directory_should_retur_value_from_get(self, mock_get):
        mock_get.return_value = "temporary directory"

        actual = get_temporary_directory()

        self.assertEqual("temporary directory", actual)

    @patch("config_rpm_maker.config.get")
    def test_get_log_level_should_use_key_for_log_level(self, mock_get):
        mock_get.return_value = "DEBUG"

        get_log_level()

        mock_get.assert_called_once_with('log_level', DEFAULT_LOG_LEVEL)

    @patch("config_rpm_maker.config.get")
    def test_get_log_level_should_return_debug_log_level(self, mock_get):
        mock_get.return_value = "DEBUG"

        actual = get_log_level()

        self.assertEqual(DEBUG, actual)

    @patch("config_rpm_maker.config.get")
    def test_get_log_level_should_return_error_log_level(self, mock_get):
        mock_get.return_value = "ERROR"

        actual = get_log_level()

        self.assertEqual(ERROR, actual)

    @patch("config_rpm_maker.config.get")
    def test_get_log_level_should_return_info_log_level(self, mock_get):
        mock_get.return_value = "INFO"

        actual = get_log_level()

        self.assertEqual(INFO, actual)

    @patch("config_rpm_maker.config.get")
    def test_get_log_level_should_raise_exception_when_strange_log_level_given(self, mock_get):
        mock_get.return_value = "FOO"

        self.assertRaises(ConfigException, get_log_level)

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
from StringIO import StringIO
from unittest import TestCase

from config_rpm_maker import config
from config_rpm_maker.config import (DEFAULT_LOG_LEVEL,
                                     DEFAULT_CONFIGURATION_FILE_PATH,
                                     ENVIRONMENT_VARIABLE_KEY_CONFIGURATION_FILE,
                                     ConfigException,
                                     get_configuration,
                                     get_log_level,
                                     get_temporary_directory,
                                     get_configuration_file_path,
                                     load_configuration_file,
                                     setvalue,
                                     set_properties)


class GetProperties(TestCase):

    @patch('config_rpm_maker.config._properties')
    def test_should_return_configuration(self, mock_configuration):

        actual_configuration = get_configuration()

        self.assertEqual(mock_configuration, actual_configuration)


class SetPropertiesTests(TestCase):

    @patch('config_rpm_maker.config._properties')
    def test_should_set_configuration_properties(self, mock_properties):

        fake_properties = {}

        set_properties(fake_properties)

        self.assertEqual(config._properties, fake_properties)


class GetConfigurationFilePath(TestCase):

    @patch('config_rpm_maker.config._configuration_file_path')
    def test_should_return_configuration(self, mock_configuration_file_path):

        actual_configuration_file_path = get_configuration_file_path()

        self.assertEqual(mock_configuration_file_path, actual_configuration_file_path)


class LoadConfigurationTests(TestCase):

    @patch('config_rpm_maker.config.exists')
    @patch('config_rpm_maker.config.environ')
    def test_should_raise_exception_if_configuration_file_does_not_exist(self, mock_environ, mock_exists):

        mock_exists.return_value = False

        self.assertRaises(ConfigException, load_configuration_file)

    @patch('config_rpm_maker.config._configuration_file_path')
    @patch('config_rpm_maker.config.exists')
    @patch('config_rpm_maker.config.environ')
    def test_should_use_default_configuration_file_path_if_no_environment_variable_is_set(self, mock_environ, mock_exists, mock_file_path):

        mock_exists.return_value = False

        self.assertRaises(ConfigException, load_configuration_file)

        mock_environ.get.assert_called_with(ENVIRONMENT_VARIABLE_KEY_CONFIGURATION_FILE, DEFAULT_CONFIGURATION_FILE_PATH)

    @patch('config_rpm_maker.config.set_properties')
    @patch('config_rpm_maker.config.yaml')
    @patch('__builtin__.open')
    @patch('config_rpm_maker.config.exists')
    @patch('config_rpm_maker.config.environ')
    def test_load_configuration_file_if_it_exists(self, mock_environ, mock_exists, mock_open, mock_yaml, mock_set_properties):

        mock_exists.return_value = True
        fake_file = self._create_fake_file()
        mock_open.return_value = fake_file

        load_configuration_file()

        mock_yaml.load.assert_called_with(fake_file)

    @patch('config_rpm_maker.config.set_properties')
    @patch('config_rpm_maker.config.yaml')
    @patch('__builtin__.open')
    @patch('config_rpm_maker.config.exists')
    @patch('config_rpm_maker.config.environ')
    def test_should_use_loaded_configuration_as_properties(self, mock_environ, mock_exists, mock_open, mock_yaml, mock_set_properties):

        mock_exists.return_value = True
        fake_file = self._create_fake_file()
        mock_open.return_value = fake_file
        mock_properties = {}
        mock_yaml.load.return_value = mock_properties

        load_configuration_file()

        mock_set_properties.assert_called_with(mock_properties)

    @patch('config_rpm_maker.config.yaml')
    @patch('__builtin__.open')
    @patch('config_rpm_maker.config.exists')
    @patch('config_rpm_maker.config.environ')
    def test_should_raise_ConfigException_when_loading_fails(self, mock_environ, mock_exists, mock_open, mock_yaml):

        mock_exists.return_value = True
        fake_file = self._create_fake_file()
        mock_open.return_value = fake_file
        mock_yaml.load.side_effect = Exception()

        self.assertRaises(ConfigException, load_configuration_file)

    def _create_fake_file(self):
        class FakeFile(StringIO):
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

        return FakeFile()


class SetValueTests(TestCase):

    def test_should_raise_configuration_exception_when_trying_to_set_value_without_name(self):

        self.assertRaises(ConfigException, setvalue, name=None, value='123')

    @patch('config_rpm_maker.config.get_configuration')
    @patch('config_rpm_maker.config.load_configuration_file')
    def test_should_load_configuration_if_no_configuration_properties_are_empty(self, mock_load_configuration_file, mock_get_configuration):

        def set_configuration_properties():
            mock_get_configuration.return_value = {}
        mock_load_configuration_file.side_effect = set_configuration_properties
        mock_get_configuration.return_value = None

        setvalue('abc', '123')

        mock_load_configuration_file.assert_called_with()

    def test_should_set_value_of_configuration_properties(self):

        setvalue('abc', '123')

        self.assertEqual('123', config._properties['abc'])


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

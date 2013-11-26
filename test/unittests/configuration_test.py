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
                                     ConfigurationValidationException,
                                     _determine_configuration_file_path,
                                     get_properties,
                                     get_log_level,
                                     get_temporary_directory,
                                     get_file_path_of_loaded_configuration,
                                     load_configuration_file,
                                     setvalue,
                                     set_properties,
                                     _load_configuration_properties_from_yaml_file,
                                     _set_file_path_of_loaded_configuration,
                                     _validate_loaded_configuration_properties)


class GetProperties(TestCase):

    @patch('config_rpm_maker.config._properties')
    def test_should_return_configuration(self, mock_configuration):

        actual_configuration = get_properties()

        self.assertEqual(mock_configuration, actual_configuration)


class SetPropertiesTests(TestCase):

    @patch('config_rpm_maker.config._properties')
    def test_should_set_configuration_properties(self, mock_properties):

        fake_properties = {}

        set_properties(fake_properties)

        self.assertEqual(config._properties, fake_properties)


class GetFilePathOfLoadedConfiguration(TestCase):

    @patch('config_rpm_maker.config._file_path_of_loaded_configuration')
    def test_should_return_configuration(self, mock_configuration_file_path):

        actual_configuration_file_path = get_file_path_of_loaded_configuration()

        self.assertEqual(mock_configuration_file_path, actual_configuration_file_path)


class SetFilePathOfLoadedConfigurationTests(TestCase):

    @patch('config_rpm_maker.config._file_path_of_loaded_configuration')
    def test_should_set_file_path_of_loaded_configuration(self, mock_file_path_of_loaded_configuration):

        fake_file_path_to_configuration_file = 'path-to-configuration-file'

        _set_file_path_of_loaded_configuration(fake_file_path_to_configuration_file)

        self.assertEqual(config._file_path_of_loaded_configuration, fake_file_path_to_configuration_file)


class DetermineConfigurationFilePathTest(TestCase):

    @patch('config_rpm_maker.config.environ')
    def test_should_use_default_configuration_file_path_if_no_environment_variable_is_set(self, mock_environ):

        _determine_configuration_file_path()

        mock_environ.get.assert_called_with(ENVIRONMENT_VARIABLE_KEY_CONFIGURATION_FILE, DEFAULT_CONFIGURATION_FILE_PATH)

    @patch('config_rpm_maker.config.environ')
    def test_should_return_actual_determined_file_path(self, mock_environ):

        mock_environ.get.return_value = 'path-to-configuration-file'

        actual_file_path = _determine_configuration_file_path()

        self.assertEqual('path-to-configuration-file', actual_file_path)


class LoadConfigurationPropertiesFromYamlFileTests(TestCase):

    @patch('config_rpm_maker.config.set_properties')
    @patch('config_rpm_maker.config.yaml')
    @patch('__builtin__.open')
    def test_should_open_file_as_specified_in_argument(self, mock_open, mock_yaml, mock_set_properties):

        fake_file = self._create_fake_file()
        mock_open.return_value = fake_file
        mock_properties = {}
        mock_yaml.load.return_value = mock_properties

        _load_configuration_properties_from_yaml_file('path-to-configuration-file')

        mock_open.assert_called_with('path-to-configuration-file')

    @patch('config_rpm_maker.config._set_file_path_of_loaded_configuration')
    @patch('config_rpm_maker.config.yaml')
    @patch('__builtin__.open')
    def test_should_set_file_path_of_loaded_configuration(self, mock_open, mock_yaml, mock_set_file_path_of_loaded_configuration):

        fake_file = self._create_fake_file()
        mock_open.return_value = fake_file
        mock_properties = {}
        mock_yaml.load.return_value = mock_properties

        _load_configuration_properties_from_yaml_file('path-to-configuration-file')

        mock_set_file_path_of_loaded_configuration.assert_called_with('path-to-configuration-file')

    @patch('config_rpm_maker.config.yaml')
    @patch('__builtin__.open')
    def test_should_raise_ConfigException_when_loading_fails(self, mock_open, mock_yaml):

        fake_file = self._create_fake_file()
        mock_open.return_value = fake_file
        mock_yaml.load.side_effect = Exception()

        self.assertRaises(ConfigException, _load_configuration_properties_from_yaml_file, 'path-to-configuration-file')

    @patch('config_rpm_maker.config._set_file_path_of_loaded_configuration')
    @patch('config_rpm_maker.config.yaml')
    @patch('__builtin__.open')
    def test_return_raw_loaded_properties(self, mock_open, mock_yaml, mock_set_file_path_of_loaded_configuration):

        fake_file = self._create_fake_file()
        mock_open.return_value = fake_file
        mock_properties = {'foo': 'bar'}
        mock_yaml.load.return_value = mock_properties

        actual_properties = _load_configuration_properties_from_yaml_file('path-to-configuration-file')

        self.assertEqual({'foo': 'bar'}, actual_properties)

    def _create_fake_file(self):
        class FakeFile(StringIO):
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

        return FakeFile()


class ValidateLoadedConfigurationPropertiesTest(TestCase):

    @patch('config_rpm_maker.config.LOGGER')
    def test_should_log_that_configuration_properties_are_empty(self, mock_logger):

        self.assertRaises(ConfigurationValidationException, _validate_loaded_configuration_properties, None)

    @patch('config_rpm_maker.config.LOGGER')
    def test_should_pass_through_if_some_configuration_properties_are_given(self, mock_logger):

        _validate_loaded_configuration_properties({'foo': 'bar'})

    @patch('config_rpm_maker.config.LOGGER')
    def test_should_return_valid_properties(self, mock_logger):

        properties = {'foo': 'bar'}

        actual_properties = _validate_loaded_configuration_properties(properties)

        self.assertEqual(properties, actual_properties)


class LoadConfigurationFileTests(TestCase):

    @patch('config_rpm_maker.config.exists')
    @patch('config_rpm_maker.config.environ')
    def test_should_raise_exception_if_configuration_file_does_not_exist(self, mock_environ, mock_exists):

        mock_exists.return_value = False

        self.assertRaises(ConfigException, load_configuration_file)

    @patch('config_rpm_maker.config.exists')
    @patch('config_rpm_maker.config._determine_configuration_file_path')
    def test_should_determine_the_configuration_file_path(self, mock_determine_configuration_file_path, mock_exists):

        mock_exists.return_value = False

        self.assertRaises(ConfigException, load_configuration_file)

        mock_determine_configuration_file_path.assert_called_with()

    @patch('config_rpm_maker.config._validate_loaded_configuration_properties')
    @patch('config_rpm_maker.config._load_configuration_properties_from_yaml_file')
    @patch('config_rpm_maker.config.exists')
    @patch('config_rpm_maker.config._determine_configuration_file_path')
    def test_check_if_the_determined_configuration_file_path_exists(self, mock_determine_configuration_file_path, mock_exists, mock_load_configuration_properties_from_yaml_file, mock_validate_loaded_configuration_properties):

        mock_determine_configuration_file_path.return_value = 'path-to-configuration-file'
        mock_exists.return_value = True

        load_configuration_file()

        mock_exists.assert_called_with('path-to-configuration-file')

    @patch('config_rpm_maker.config._validate_loaded_configuration_properties')
    @patch('config_rpm_maker.config._load_configuration_properties_from_yaml_file')
    @patch('config_rpm_maker.config.exists')
    @patch('config_rpm_maker.config._determine_configuration_file_path')
    def test_load_configuration_file_if_it_exists(self, mock_determine_configuration_file_path, mock_exists, mock_load_configuration_properties_from_yaml_file, mock_validate_loaded_configuration_properties):

        mock_determine_configuration_file_path.return_value = 'path-to-configuration-file'
        mock_exists.return_value = True

        load_configuration_file()

        mock_load_configuration_properties_from_yaml_file.assert_called_with('path-to-configuration-file')

    @patch('config_rpm_maker.config._validate_loaded_configuration_properties')
    @patch('config_rpm_maker.config._load_configuration_properties_from_yaml_file')
    @patch('config_rpm_maker.config.exists')
    @patch('config_rpm_maker.config._determine_configuration_file_path')
    def test_should_validate_loaded_configuration_properties(self, mock_determine_configuration_file_path, mock_exists, mock_load_configuration_properties_from_yaml_file, mock_validate_loaded_configuration_properties):

        mock_determine_configuration_file_path.return_value = 'path-to-configuration-file'
        mock_exists.return_value = True
        mock_properties = {'foo': 'bar'}
        mock_load_configuration_properties_from_yaml_file.return_value = mock_properties

        load_configuration_file()

        mock_validate_loaded_configuration_properties.assert_called_with(mock_properties)

    @patch('config_rpm_maker.config.set_properties')
    @patch('config_rpm_maker.config._validate_loaded_configuration_properties')
    @patch('config_rpm_maker.config._load_configuration_properties_from_yaml_file')
    @patch('config_rpm_maker.config.exists')
    @patch('config_rpm_maker.config._determine_configuration_file_path')
    def test_should_set_properties_to_valid_values(self, mock_determine_configuration_file_path, mock_exists, mock_load_configuration_properties_from_yaml_file, mock_validate_loaded_configuration_properties, mock_set_properties):

        mock_determine_configuration_file_path.return_value = 'path-to-configuration-file'
        mock_exists.return_value = True
        fake_raw_properties = {'foo': 'bar'}
        mock_load_configuration_properties_from_yaml_file.return_value = fake_raw_properties
        fake_valid_properties = {'spam': 'eggs'}
        mock_validate_loaded_configuration_properties.return_value = fake_valid_properties

        load_configuration_file()

        mock_set_properties.assert_called_with(fake_valid_properties)


class SetValueTests(TestCase):

    def test_should_raise_configuration_exception_when_trying_to_set_value_without_name(self):

        self.assertRaises(ConfigException, setvalue, name=None, value='123')

    @patch('config_rpm_maker.config.get_properties')
    @patch('config_rpm_maker.config.load_configuration_file')
    def test_should_load_configuration_if_no_configuration_properties_are_empty(self, mock_load_configuration_file, mock_get_configuration):

        def set_configuration_properties():
            mock_get_configuration.return_value = {}
        mock_load_configuration_file.side_effect = set_configuration_properties
        mock_get_configuration.return_value = None

        setvalue('abc', '123')

        mock_load_configuration_file.assert_called_with()

    @patch('config_rpm_maker.config.get_properties')
    def test_should_set_value_of_configuration_properties(self, mock_get_properties):
        fake_properties = {}
        mock_get_properties.return_value = fake_properties

        setvalue('abc', '123')

        self.assertEqual('123', fake_properties['abc'])


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

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

from unittest_support import UnitTests
from config_rpm_maker import config
from config_rpm_maker.config import (ConfigurationException,
                                     DEFAULT_CONFIGURATION_FILE_PATH,
                                     ENVIRONMENT_VARIABLE_KEY_CONFIGURATION_FILE,
                                     KEY_ALLOW_UNKNOWN_HOSTS,
                                     KEY_CONFIG_RPM_PREFIX,
                                     KEY_CONFIG_VIEWER_ONLY,
                                     KEY_CONFIG_VIEWER_HOSTS_DIR,
                                     KEY_CUSTOM_DNS_SEARCHLIST,
                                     KEY_ERROR_LOG_DIRECTORY,
                                     KEY_ERROR_LOG_URL,
                                     KEY_LOG_LEVEL,
                                     KEY_NO_CLEAN_UP,
                                     KEY_MAX_FAILED_HOSTS,
                                     KEY_MAX_FILE_SIZE,
                                     KEY_PATH_TO_SPEC_FILE,
                                     KEY_REPO_PACKAGES_REGEX,
                                     KEY_RPM_UPLOAD_CHUNK_SIZE,
                                     KEY_RPM_UPLOAD_COMMAND,
                                     KEY_SVN_PATH_TO_CONFIGURATION,
                                     KEY_THREAD_COUNT,
                                     KEY_TEMP_DIR,
                                     KEY_VERBOSE,
                                     build_config_viewer_host_directory,
                                     get_file_path_of_loaded_configuration,
                                     get_properties,
                                     get,
                                     load_configuration_file,
                                     set_property,
                                     set_properties,
                                     _determine_configuration_file_path,
                                     _ensure_valid_log_level,
                                     _ensure_is_a_boolean_value,
                                     _ensure_is_an_integer,
                                     _ensure_is_a_string,
                                     _ensure_is_a_string_or_none,
                                     _ensure_is_a_list_of_strings,
                                     _ensure_repo_packages_regex_is_a_valid_regular_expression,
                                     _ensure_properties_are_valid,
                                     _load_configuration_properties_from_yaml_file,
                                     _set_file_path_of_loaded_configuration)


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


class LoadConfigurationPropertiesFromYamlFileTests(UnitTests):

    @patch('config_rpm_maker.config.set_properties')
    @patch('config_rpm_maker.config.yaml')
    @patch('__builtin__.open')
    def test_should_open_file_as_specified_in_argument(self, mock_open, mock_yaml, mock_set_properties):

        fake_file = self.create_fake_file()
        mock_open.return_value = fake_file
        mock_properties = {}
        mock_yaml.load.return_value = mock_properties

        _load_configuration_properties_from_yaml_file('path-to-configuration-file')

        mock_open.assert_called_with('path-to-configuration-file')

    @patch('config_rpm_maker.config._set_file_path_of_loaded_configuration')
    @patch('config_rpm_maker.config.yaml')
    @patch('__builtin__.open')
    def test_should_set_file_path_of_loaded_configuration(self, mock_open, mock_yaml, mock_set_file_path_of_loaded_configuration):

        fake_file = self.create_fake_file()
        mock_open.return_value = fake_file
        mock_properties = {}
        mock_yaml.load.return_value = mock_properties

        _load_configuration_properties_from_yaml_file('path-to-configuration-file')

        mock_set_file_path_of_loaded_configuration.assert_called_with('path-to-configuration-file')

    @patch('config_rpm_maker.config.yaml')
    @patch('__builtin__.open')
    def test_should_raise_ConfigurationException_when_loading_fails(self, mock_open, mock_yaml):

        fake_file = self.create_fake_file()
        mock_open.return_value = fake_file
        mock_yaml.load.side_effect = Exception()

        self.assertRaises(ConfigurationException, _load_configuration_properties_from_yaml_file, 'path-to-configuration-file')

    @patch('config_rpm_maker.config._set_file_path_of_loaded_configuration')
    @patch('config_rpm_maker.config.yaml')
    @patch('__builtin__.open')
    def test_should_return_raw_loaded_properties(self, mock_open, mock_yaml, mock_set_file_path_of_loaded_configuration):

        fake_file = self.create_fake_file()
        mock_open.return_value = fake_file
        mock_properties = {'foo': 'bar'}
        mock_yaml.load.return_value = mock_properties

        actual_properties = _load_configuration_properties_from_yaml_file('path-to-configuration-file')

        self.assertEqual({'foo': 'bar'}, actual_properties)


class EnsurePropertiesAreValidTest(TestCase):

    @patch('config_rpm_maker.config.LOGGER')
    def test_should_log_that_configuration_properties_are_empty(self, mock_logger):

        _ensure_properties_are_valid(None)

        mock_logger.warn.assert_called_with('Loaded configuration properties are empty.')

    @patch('config_rpm_maker.config.LOGGER')
    def test_should_pass_through_if_some_configuration_properties_are_given(self, mock_logger):

        _ensure_properties_are_valid({'allow_unknown_hosts': True})

    @patch('config_rpm_maker.config._ensure_valid_log_level')
    def test_should_return_log_level_valid_properties(self, mock_ensure_valid_log_level):

        mock_ensure_valid_log_level.return_value = 'valid_log_level'
        properties = {'log_level': 'debug'}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('valid_log_level', actual_properties[KEY_LOG_LEVEL])

    @patch('config_rpm_maker.config._ensure_valid_log_level')
    def test_should_return_default_log_level_when_no_log_level_defined(self, mock_ensure_valid_log_level):

        mock_ensure_valid_log_level.return_value = 'valid_log_level'
        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('valid_log_level', actual_properties[KEY_LOG_LEVEL])

    @patch('config_rpm_maker.config._ensure_is_a_boolean_value')
    def test_should_return_property_allow_unkown_hosts(self, mock_ensure_valid_allow_unknown_hosts):

        mock_ensure_valid_allow_unknown_hosts.return_value = False
        properties = {'allow_unknown_hosts': False}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertFalse(actual_properties[KEY_ALLOW_UNKNOWN_HOSTS])
        mock_ensure_valid_allow_unknown_hosts.assert_called_with(KEY_ALLOW_UNKNOWN_HOSTS, False)

    def test_should_return_default_property_for_allow_unkown_hosts(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertTrue(actual_properties[KEY_ALLOW_UNKNOWN_HOSTS])

    def test_should_return_default_for_allow_unknown_hosts_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertTrue(actual_properties[KEY_ALLOW_UNKNOWN_HOSTS])

    @patch('config_rpm_maker.config._ensure_is_a_string')
    def test_should_return_property_config_rpm_prefix(self, mock_ensure_is_a_string):

        mock_ensure_is_a_string.return_value = 'valid string'
        properties = {'config_rpm_prefix': 'spam-eggs'}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('valid string', actual_properties[KEY_CONFIG_RPM_PREFIX])
        mock_ensure_is_a_string.assert_any_call(KEY_CONFIG_RPM_PREFIX, 'spam-eggs')

    def test_should_return_default_for_config_rpm_prefix_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('yadt-config-', actual_properties[KEY_CONFIG_RPM_PREFIX])

    @patch('config_rpm_maker.config._ensure_is_a_list_of_strings')
    def test_should_return_property_custom_dns_searchlist(self, mock_ensure_is_a_list_of_strings):

        mock_ensure_is_a_list_of_strings.return_value = ['a', 'valid', 'list', 'of', 'strings']
        properties = {'custom_dns_searchlist': ['a', 'list', 'of', 'dns', 'servers']}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual(['a', 'valid', 'list', 'of', 'strings'], actual_properties[KEY_CUSTOM_DNS_SEARCHLIST])
        mock_ensure_is_a_list_of_strings.assert_any_call(KEY_CUSTOM_DNS_SEARCHLIST, ['a', 'list', 'of', 'dns', 'servers'])

    def test_should_return_default_for_custom_dns_searchlist_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual([], actual_properties[KEY_CUSTOM_DNS_SEARCHLIST])

    @patch('config_rpm_maker.config._ensure_is_a_string')
    def test_should_return_property_error_log_dir(self, mock_ensure_is_a_string):

        mock_ensure_is_a_string.return_value = 'the valid error log'
        properties = {'error_log_dir': 'error-spam-eggs/logs'}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('the valid error log', actual_properties[KEY_ERROR_LOG_DIRECTORY])
        mock_ensure_is_a_string.assert_any_call(KEY_ERROR_LOG_DIRECTORY, 'error-spam-eggs/logs')

    def test_should_return_default_for_error_log_dir_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('', actual_properties[KEY_ERROR_LOG_DIRECTORY])

    @patch('config_rpm_maker.config._ensure_is_a_string')
    def test_should_return_property_error_url_dir(self, mock_ensure_is_string):

        mock_ensure_is_string.return_value = 'a valid error log url'
        properties = {'error_log_url': 'error-spam-eggs-url'}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('a valid error log url', actual_properties[KEY_ERROR_LOG_URL])
        mock_ensure_is_string.assert_any_call(KEY_ERROR_LOG_URL, 'error-spam-eggs-url')

    def test_should_return_default_for_error_log_url_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('', actual_properties[KEY_ERROR_LOG_URL])

    @patch('config_rpm_maker.config._ensure_is_a_string')
    def test_should_return_path_to_spec_file(self, mock_ensure_is_a_string):

        mock_ensure_is_a_string.return_value = 'a valid spec file'
        properties = {'path_to_spec_file': 'spam-eggs.speck'}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('a valid spec file', actual_properties[KEY_PATH_TO_SPEC_FILE])
        mock_ensure_is_a_string.assert_any_call(KEY_PATH_TO_SPEC_FILE, 'spam-eggs.speck')

    def test_should_return_default_for_path_to_spec_file_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('default.spec', actual_properties[KEY_PATH_TO_SPEC_FILE])

    @patch('config_rpm_maker.config._ensure_repo_packages_regex_is_a_valid_regular_expression')
    def test_should_return_repo_packages_regex(self, mock_ensure_repo_packages_regex_is_valid_or_none):

        mock_ensure_repo_packages_regex_is_valid_or_none.return_value = 'a valid regex'
        properties = {'repo_packages_regex': '.*-spam-.*'}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('a valid regex', actual_properties[KEY_REPO_PACKAGES_REGEX])
        mock_ensure_repo_packages_regex_is_valid_or_none.assert_any_call('.*-spam-.*')

    def test_should_return_default_for_repo_packages_regex_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual(".*-repo.*", actual_properties[KEY_REPO_PACKAGES_REGEX])

    @patch('config_rpm_maker.config._ensure_is_an_integer')
    def test_should_return_rpm_upload_chunk_size(self, mock_ensure_is_an_integer):

        mock_ensure_is_an_integer.return_value = 123
        properties = {'rpm_upload_chunk_size': 5}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual(123, actual_properties[KEY_RPM_UPLOAD_CHUNK_SIZE])
        mock_ensure_is_an_integer.assert_any_call(KEY_RPM_UPLOAD_CHUNK_SIZE, 5)

    def test_should_return_default_for_rpm_upload_chunk_size_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual(10, actual_properties[KEY_RPM_UPLOAD_CHUNK_SIZE])

    @patch('config_rpm_maker.config._ensure_is_a_string_or_none')
    def test_should_return_rpm_upload_command_regex(self, mock_ensure_is_a_string_or_none):

        mock_ensure_is_a_string_or_none.return_value = 'a valid upload command'
        properties = {'rpm_upload_cmd': '/usr/bin/rm'}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('a valid upload command', actual_properties[KEY_RPM_UPLOAD_COMMAND])
        mock_ensure_is_a_string_or_none.assert_any_call(KEY_RPM_UPLOAD_COMMAND, '/usr/bin/rm')

    def test_should_return_default_for_rpm_upload_command_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual(None, actual_properties[KEY_RPM_UPLOAD_COMMAND])

    @patch('config_rpm_maker.config._ensure_is_a_string')
    def test_should_return_svn_path_to_config(self, mock_ensure_is_a_string):

        mock_ensure_is_a_string.return_value = 'a valid svn path'
        properties = {'svn_path_to_config': '/configuration'}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('a valid svn path', actual_properties[KEY_SVN_PATH_TO_CONFIGURATION])
        mock_ensure_is_a_string.assert_any_call(KEY_SVN_PATH_TO_CONFIGURATION, '/configuration')

    def test_should_return_default_for_svn_path_to_config_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('/config', actual_properties[KEY_SVN_PATH_TO_CONFIGURATION])

    @patch('config_rpm_maker.config._ensure_is_an_integer')
    def test_should_return_thread_count(self, mock_ensure_is_an_integer):

        mock_ensure_is_an_integer.return_value = 123
        properties = {'thread_count': 10}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual(123, actual_properties[KEY_THREAD_COUNT])
        mock_ensure_is_an_integer.assert_any_call(KEY_THREAD_COUNT, 10)

    def test_should_return_default_for_thread_count_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual(1, actual_properties[KEY_THREAD_COUNT])

    @patch('config_rpm_maker.config._ensure_is_a_string')
    def test_should_return_temp_dir(self, mock_ensure_is_a_string):

        mock_ensure_is_a_string.return_value = 'a valid temporary directory'
        properties = {'temp_dir': 'target/tmp'}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('a valid temporary directory', actual_properties[KEY_TEMP_DIR])
        mock_ensure_is_a_string.assert_any_call(KEY_TEMP_DIR, 'target/tmp')

    def test_should_return_default_for_temp_dir_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('/tmp', actual_properties[KEY_TEMP_DIR])

    @patch('config_rpm_maker.config._ensure_is_a_string')
    def test_should_return_config_viewer_hosts_dir(self, mock_ensure_is_a_string):

        mock_ensure_is_a_string.return_value = 'a valid string'
        properties = {'config_viewer_hosts_dir': 'target/tmp/configviewer'}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('a valid string', actual_properties[KEY_CONFIG_VIEWER_HOSTS_DIR])
        mock_ensure_is_a_string.assert_any_call(KEY_CONFIG_VIEWER_HOSTS_DIR, 'target/tmp/configviewer')

    def test_should_return_default_for_config_viewer_hosts_dir_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('/tmp', actual_properties[KEY_CONFIG_VIEWER_HOSTS_DIR])

    @patch('config_rpm_maker.config.LOGGER')
    def test_should_warn_when_raw_properties_contain_an_unknown_property_name(self, mock_logger):

        properties = {'foo_spam': '/usr/bin/tralala'}

        _ensure_properties_are_valid(properties)

        mock_logger.warn.assert_called_with('Unknown configuration propertie(s) found: foo_spam')

    @patch('config_rpm_maker.config._ensure_is_an_integer')
    def test_should_return_max_file_size(self, mock_ensure_is_an_integer):

        mock_ensure_is_an_integer.return_value = 123000000
        properties = {'max_file_size': 10000000}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual(123000000, actual_properties[KEY_MAX_FILE_SIZE])
        mock_ensure_is_an_integer.assert_any_call(KEY_MAX_FILE_SIZE, 10000000)

    def test_should_return_default_for_max_file_size_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual(102400, actual_properties[KEY_MAX_FILE_SIZE])

    @patch('config_rpm_maker.config._ensure_is_an_integer')
    def test_should_return_max_failed_hosts(self, mock_ensure_is_an_integer):

        mock_ensure_is_an_integer.return_value = 5
        properties = {'max_failed_hosts': 3}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual(5, actual_properties[KEY_MAX_FAILED_HOSTS])
        mock_ensure_is_an_integer.assert_any_call(KEY_MAX_FAILED_HOSTS, 3)

    def test_should_return_default_for_max_failed_hosts_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual(3, actual_properties[KEY_MAX_FAILED_HOSTS])

    def test_should_return_default_config_viewer_only(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertFalse(actual_properties[KEY_CONFIG_VIEWER_ONLY])

    def test_should_return_default_verbose(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertFalse(actual_properties[KEY_VERBOSE])

    def test_should_return_default_no_clean_up(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertFalse(actual_properties[KEY_NO_CLEAN_UP])


class LoadConfigurationFileTests(TestCase):

    @patch('config_rpm_maker.config.exists')
    @patch('config_rpm_maker.config.environ')
    def test_should_raise_exception_if_configuration_file_does_not_exist(self, mock_environ, mock_exists):

        mock_exists.return_value = False

        self.assertRaises(ConfigurationException, load_configuration_file)

    @patch('config_rpm_maker.config.exists')
    @patch('config_rpm_maker.config._determine_configuration_file_path')
    def test_should_determine_the_configuration_file_path(self, mock_determine_configuration_file_path, mock_exists):

        mock_exists.return_value = False

        self.assertRaises(ConfigurationException, load_configuration_file)

        mock_determine_configuration_file_path.assert_called_with()

    @patch('config_rpm_maker.config._ensure_properties_are_valid')
    @patch('config_rpm_maker.config._load_configuration_properties_from_yaml_file')
    @patch('config_rpm_maker.config.exists')
    @patch('config_rpm_maker.config._determine_configuration_file_path')
    def test_should_check_if_the_determined_configuration_file_path_exists(self, mock_determine_configuration_file_path, mock_exists, mock_load_configuration_properties_from_yaml_file, mock_ensure_properties_are_valid):

        mock_determine_configuration_file_path.return_value = 'path-to-configuration-file'
        mock_exists.return_value = True

        load_configuration_file()

        mock_exists.assert_called_with('path-to-configuration-file')

    @patch('config_rpm_maker.config._ensure_properties_are_valid')
    @patch('config_rpm_maker.config._load_configuration_properties_from_yaml_file')
    @patch('config_rpm_maker.config.exists')
    @patch('config_rpm_maker.config._determine_configuration_file_path')
    def test_should_load_configuration_file_if_it_exists(self, mock_determine_configuration_file_path, mock_exists, mock_load_configuration_properties_from_yaml_file, mock_ensure_properties_are_valid):

        mock_determine_configuration_file_path.return_value = 'path-to-configuration-file'
        mock_exists.return_value = True

        load_configuration_file()

        mock_load_configuration_properties_from_yaml_file.assert_called_with('path-to-configuration-file')

    @patch('config_rpm_maker.config._ensure_properties_are_valid')
    @patch('config_rpm_maker.config._load_configuration_properties_from_yaml_file')
    @patch('config_rpm_maker.config.exists')
    @patch('config_rpm_maker.config._determine_configuration_file_path')
    def test_should_ensure_properties_are_valid(self, mock_determine_configuration_file_path, mock_exists, mock_load_configuration_properties_from_yaml_file, mock_ensure_properties_are_valid):

        mock_determine_configuration_file_path.return_value = 'path-to-configuration-file'
        mock_exists.return_value = True
        mock_properties = {'foo': 'bar'}
        mock_load_configuration_properties_from_yaml_file.return_value = mock_properties

        load_configuration_file()

        mock_ensure_properties_are_valid.assert_called_with(mock_properties)

    @patch('config_rpm_maker.config.set_properties')
    @patch('config_rpm_maker.config._ensure_properties_are_valid')
    @patch('config_rpm_maker.config._load_configuration_properties_from_yaml_file')
    @patch('config_rpm_maker.config.exists')
    @patch('config_rpm_maker.config._determine_configuration_file_path')
    def test_should_set_properties_to_valid_values(self, mock_determine_configuration_file_path, mock_exists, mock_load_configuration_properties_from_yaml_file, mock_ensure_properties_are_valid, mock_set_properties):

        mock_determine_configuration_file_path.return_value = 'path-to-configuration-file'
        mock_exists.return_value = True
        fake_raw_properties = {'foo': 'bar'}
        mock_load_configuration_properties_from_yaml_file.return_value = fake_raw_properties
        fake_valid_properties = {'spam': 'eggs'}
        mock_ensure_properties_are_valid.return_value = fake_valid_properties

        load_configuration_file()

        mock_set_properties.assert_called_with(fake_valid_properties)


class GetPropertyTests(TestCase):

    @patch('config_rpm_maker.config.get_properties')
    @patch('config_rpm_maker.config.load_configuration_file')
    def test_should_load_configuration_file_when_no_properties_available(self, mock_load_configuration_file, mock_properties):

        mock_properties.return_value = None

        def mock_set_properties():
            mock_properties.return_value = {KEY_MAX_FILE_SIZE: 12345}

        mock_load_configuration_file.side_effect = mock_set_properties

        get(KEY_MAX_FILE_SIZE)

        mock_load_configuration_file.assert_called_with()

    @patch('config_rpm_maker.config.get_properties')
    def test_should_raise_exception_when_property_key_not_in_properties(self, mock_properties):

        mock_properties.return_value = {}

        self.assertRaises(ConfigurationException, get, KEY_MAX_FILE_SIZE)

    @patch('config_rpm_maker.config.get_properties')
    def test_should_return_value_of_property_when_in_properties(self, mock_properties):

        mock_properties.return_value = {KEY_MAX_FILE_SIZE: 28374}

        actual = get(KEY_MAX_FILE_SIZE)

        self.assertEqual(28374, actual)


class SetValueTests(TestCase):

    def test_should_raise_configuration_exception_when_trying_to_set_value_without_name(self):

        self.assertRaises(ConfigurationException, set_property, name=None, value='123')

    @patch('config_rpm_maker.config.get_properties')
    @patch('config_rpm_maker.config.load_configuration_file')
    def test_should_load_configuration_if_no_configuration_properties_are_empty(self, mock_load_configuration_file, mock_get_configuration):

        def set_configuration_properties():
            mock_get_configuration.return_value = {}
        mock_load_configuration_file.side_effect = set_configuration_properties
        mock_get_configuration.return_value = None

        set_property('abc', '123')

        mock_load_configuration_file.assert_called_with()

    @patch('config_rpm_maker.config.get_properties')
    def test_should_set_value_of_configuration_properties(self, mock_get_properties):
        fake_properties = {}
        mock_get_properties.return_value = fake_properties

        set_property('abc', '123')

        self.assertEqual('123', fake_properties['abc'])


class EnsureValidLogLevelTests(TestCase):

    def test_should_raise_exception_if_given_value_is_not_a_string(self):

        self.assertRaises(ConfigurationException, _ensure_valid_log_level, 1)

    def test_should_return_debug_log_level_if_lower_debug_is_given(self):

        actual = _ensure_valid_log_level("debug")

        self.assertEqual(DEBUG, actual)

    def test_should_return_debug_log_level_if_name_contains_whitespace(self):

        actual = _ensure_valid_log_level("\tdeBug    ")

        self.assertEqual(DEBUG, actual)

    def test_should_return_debug_log_level(self):

        actual = _ensure_valid_log_level("DEBUG")

        self.assertEqual(DEBUG, actual)

    def test_should_return_error_log_level(self):

        actual = _ensure_valid_log_level("ERROR")

        self.assertEqual(ERROR, actual)

    def test_should_return_info_log_level(self):

        actual = _ensure_valid_log_level("INFO")

        self.assertEqual(INFO, actual)

    def test_should_raise_exception_when_strange_log_level_given(self):

        self.assertRaises(ConfigurationException, _ensure_valid_log_level, "FOO")


class GetConfigViewerHostDirTests(TestCase):

    @patch('config_rpm_maker.config.get')
    def test_should_return_path_to_host_directory(self, mock_get):

        mock_get.return_value = 'path-to-config-viewer-host-directory'

        actual_path = build_config_viewer_host_directory('devweb01')

        mock_get.assert_called_with(KEY_CONFIG_VIEWER_HOSTS_DIR)
        self.assertEqual('path-to-config-viewer-host-directory/devweb01', actual_path)

    @patch('config_rpm_maker.config.get')
    def test_should_return_path_and_append_a_postfix(self, mock_get):

        mock_get.return_value = 'path-to-config-viewer-host-directory'

        actual_path = build_config_viewer_host_directory('devweb01', revision='123')

        mock_get.assert_called_with(KEY_CONFIG_VIEWER_HOSTS_DIR)
        self.assertEqual('path-to-config-viewer-host-directory/devweb01.new-revision-123', actual_path)


class EnsureIsABooleanValueTests(TestCase):

    def test_should_raise_exception_if_type_is_not_boolean(self):

        self.assertRaises(ConfigurationException, _ensure_is_a_boolean_value, 'foo', 'bar')

    def test_should_return_valid_value_when_given_value_is_true(self):

        actual = _ensure_is_a_boolean_value('key', True)

        self.assertTrue(actual)

    def test_should_return_valid_value_when_given_value_is_false(self):

        actual = _ensure_is_a_boolean_value('key', False)

        self.assertFalse(actual)


class EnsureIsAString(TestCase):

    def test_should_raise_exception_if_type_is_not_string(self):

        self.assertRaises(ConfigurationException, _ensure_is_a_string, 'key', True)

    def test_should_return_given_string(self):

        actual = _ensure_is_a_string('key', 'value')

        self.assertEqual('value', actual)


class EnsureIsAInteger(TestCase):

    def test_should_raise_exception_if_type_is_not_integer(self):

        self.assertRaises(ConfigurationException, _ensure_is_an_integer, 'key', 'hello')

    def test_should_return_given_integer(self):

        actual = _ensure_is_an_integer('abc', 123)

        self.assertEqual(123, actual)


class EnsureRepoPackageRegexIsAValidRegularExpressionTests(TestCase):

    def test_should_raise_an_exception_if_given_value_is_not_of_type_string(self):

        self.assertRaises(ConfigurationException, _ensure_repo_packages_regex_is_a_valid_regular_expression, 123)

    def test_should_raise_an_exception_when_a_invalid_regex_is_given(self):

        self.assertRaises(ConfigurationException, _ensure_repo_packages_regex_is_a_valid_regular_expression, '[')

    def test_should_return_given_value_if_it_is_a_valid_regex(self):

        actual = _ensure_repo_packages_regex_is_a_valid_regular_expression(".*")

        self.assertEqual(".*", actual)


class EnsureRpmUploadCommandIsAStringOrNoneTests(TestCase):

    def test_should_raise_exception_when_given_value_is_not_a_string(self):

        self.assertRaises(ConfigurationException, _ensure_is_a_string_or_none, 'key', 123)

    def test_should_return_none_when_none_is_given(self):

        actual = _ensure_is_a_string_or_none('key', None)

        self.assertEqual(None, actual)

    def test_should_return_given_string(self):

        actual = _ensure_is_a_string_or_none('key', 'foo-spam')

        self.assertEqual('foo-spam', actual)


class EnsureIsAListOfStringsTest(TestCase):

    def test_should_raise_exception_when_given_value_is_not_a_list(self):

        self.assertRaises(ConfigurationException, _ensure_is_a_list_of_strings, 'spam', 123)

    def test_should_return_given_empty_list(self):

        actual = _ensure_is_a_list_of_strings('key', [])

        self.assertEqual([], actual)

    def test_should_raise_exception_when_a_list_with_an_integer_is_given(self):

        self.assertRaises(ConfigurationException, _ensure_is_a_list_of_strings, 'spam', [1])

    def test_should_return_given_list_with_multiple_strings(self):

        actual = _ensure_is_a_list_of_strings('key', ['one', 'two', 'three'])

        self.assertEqual(['one', 'two', 'three'], actual)

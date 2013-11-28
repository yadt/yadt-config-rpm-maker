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
from config_rpm_maker.config import (DEFAULT_CONFIGURATION_FILE_PATH,
                                     KEY_ALLOW_UNKNOWN_HOSTS,
                                     KEY_CONFIG_RPM_PREFIX,
                                     KEY_CONFIG_VIEWER_HOSTS_DIR,
                                     KEY_CUSTOM_DNS_SEARCHLIST,
                                     KEY_ERROR_LOG_DIRECTORY,
                                     KEY_ERROR_URL_DIRECTORY,
                                     KEY_LOG_LEVEL,
                                     KEY_PATH_TO_SPEC_FILE,
                                     KEY_REPO_PACKAGES_REGEX,
                                     KEY_RPM_UPLOAD_CHUNK_SIZE,
                                     KEY_RPM_UPLOAD_COMMAND,
                                     KEY_SVN_PATH_TO_CONFIGURATION,
                                     KEY_THREAD_COUNT,
                                     KEY_TEMP_DIR,
                                     ENVIRONMENT_VARIABLE_KEY_CONFIGURATION_FILE,
                                     ConfigException,
                                     ConfigurationValidationException,
                                     _ensure_valid_log_level,
                                     build_config_viewer_host_directory_by_hostname,
                                     get_file_path_of_loaded_configuration,
                                     get_properties,
                                     load_configuration_file,
                                     set_property,
                                     set_properties,
                                     _determine_configuration_file_path,
                                     _load_configuration_properties_from_yaml_file,
                                     _set_file_path_of_loaded_configuration,
                                     _ensure_properties_are_valid)


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
    def test_should_raise_ConfigException_when_loading_fails(self, mock_open, mock_yaml):

        fake_file = self.create_fake_file()
        mock_open.return_value = fake_file
        mock_yaml.load.side_effect = Exception()

        self.assertRaises(ConfigException, _load_configuration_properties_from_yaml_file, 'path-to-configuration-file')

    @patch('config_rpm_maker.config._set_file_path_of_loaded_configuration')
    @patch('config_rpm_maker.config.yaml')
    @patch('__builtin__.open')
    def test_return_raw_loaded_properties(self, mock_open, mock_yaml, mock_set_file_path_of_loaded_configuration):

        fake_file = self.create_fake_file()
        mock_open.return_value = fake_file
        mock_properties = {'foo': 'bar'}
        mock_yaml.load.return_value = mock_properties

        actual_properties = _load_configuration_properties_from_yaml_file('path-to-configuration-file')

        self.assertEqual({'foo': 'bar'}, actual_properties)


class EnsurePropertiesAreValidTest(TestCase):

    @patch('config_rpm_maker.config.LOGGER')
    def test_should_log_that_configuration_properties_are_empty(self, mock_logger):

        self.assertRaises(ConfigurationValidationException, _ensure_properties_are_valid, None)

    @patch('config_rpm_maker.config.LOGGER')
    def test_should_pass_through_if_some_configuration_properties_are_given(self, mock_logger):

        _ensure_properties_are_valid({'foo': 'bar'})

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

    def test_should_return_property_allow_unkown_hosts(self):

        properties = {'allow_unkown_hosts': True}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertTrue(actual_properties[KEY_ALLOW_UNKNOWN_HOSTS])

    def test_should_return_default_for_allow_unknown_hosts_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertTrue(actual_properties[KEY_ALLOW_UNKNOWN_HOSTS])

    def test_should_return_property_config_rpm_prefix(self):

        properties = {'config_rpm_prefix': 'spam-eggs'}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertTrue(actual_properties[KEY_CONFIG_RPM_PREFIX])

    def test_should_return_default_for_config_rpm_prefix_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('yadt-config-', actual_properties[KEY_CONFIG_RPM_PREFIX])

    def test_should_return_property_custom_dns_searchlist(self):

        properties = {'custom_dns_searchlist': ['spam-eggs']}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual(['spam-eggs'], actual_properties[KEY_CUSTOM_DNS_SEARCHLIST])

    def test_should_return_default_for_custom_dns_searchlist_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual([], actual_properties[KEY_CUSTOM_DNS_SEARCHLIST])

    def test_should_return_property_error_log_dir(self):

        properties = {'error_log_dir': 'spam-eggs'}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('spam-eggs', actual_properties[KEY_ERROR_LOG_DIRECTORY])

    def test_should_return_default_for_error_log_dir_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('', actual_properties[KEY_ERROR_LOG_DIRECTORY])

    def test_should_return_property_error_url_dir(self):

        properties = {'error_log_url': 'spam-eggs'}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('spam-eggs', actual_properties[KEY_ERROR_URL_DIRECTORY])

    def test_should_return_default_for_error_log_url_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('', actual_properties[KEY_ERROR_URL_DIRECTORY])

    def test_should_return_path_to_spec_file(self):

        properties = {'path_to_spec_file': 'spam-eggs.speck'}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('spam-eggs.speck', actual_properties[KEY_PATH_TO_SPEC_FILE])

    def test_should_return_default_for_path_to_spec_file_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('default.spec', actual_properties[KEY_PATH_TO_SPEC_FILE])

    def test_should_return_repo_packages_regex(self):

        properties = {'repo_packages_regex': 'spam-eggs.speck'}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('spam-eggs.speck', actual_properties[KEY_REPO_PACKAGES_REGEX])

    def test_should_return_default_for_repo_packages_regex_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('^yadt-.*-repos?$', actual_properties[KEY_REPO_PACKAGES_REGEX])

    def test_should_return_rpm_upload_chunk_size_regex(self):

        properties = {'rpm_upload_chunk_size': 5}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual(5, actual_properties[KEY_RPM_UPLOAD_CHUNK_SIZE])

    def test_should_return_default_for_rpm_upload_chunk_size_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual(10, actual_properties[KEY_RPM_UPLOAD_CHUNK_SIZE])

    def test_should_return_rpm_upload_command_regex(self):

        properties = {'rpm_upload_cmd': '/usr/bin/rm'}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('/usr/bin/rm', actual_properties[KEY_RPM_UPLOAD_COMMAND])

    def test_should_return_default_for_rpm_upload_command_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual(None, actual_properties[KEY_RPM_UPLOAD_COMMAND])

    def test_should_return_svn_path_to_config(self):

        properties = {'svn_path_to_config': '/configuration'}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('/configuration', actual_properties[KEY_SVN_PATH_TO_CONFIGURATION])

    def test_should_return_default_for_svn_path_to_config_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('/config', actual_properties[KEY_SVN_PATH_TO_CONFIGURATION])

    def test_should_return_thread_count(self):

        properties = {'thread_count': 10}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual(10, actual_properties[KEY_THREAD_COUNT])

    def test_should_return_default_for_thread_count_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual(1, actual_properties[KEY_THREAD_COUNT])

    def test_should_return_temp_dir(self):

        properties = {'temp_dir': 'target/tmp'}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('target/tmp', actual_properties[KEY_TEMP_DIR])

    def test_should_return_default_for_temp_dir_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('/tmp', actual_properties[KEY_TEMP_DIR])

    def test_should_return_config_viewer_hosts_dir(self):

        properties = {'config_viewer_hosts_dir': 'target/tmp/configviewer'}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('target/tmp/configviewer', actual_properties[KEY_CONFIG_VIEWER_HOSTS_DIR])

    def test_should_return_default_for_config_viewer_hosts_dir_if_not_defined(self):

        properties = {}

        actual_properties = _ensure_properties_are_valid(properties)

        self.assertEqual('/tmp', actual_properties[KEY_CONFIG_VIEWER_HOSTS_DIR])


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

    @patch('config_rpm_maker.config._ensure_properties_are_valid')
    @patch('config_rpm_maker.config._load_configuration_properties_from_yaml_file')
    @patch('config_rpm_maker.config.exists')
    @patch('config_rpm_maker.config._determine_configuration_file_path')
    def test_check_if_the_determined_configuration_file_path_exists(self, mock_determine_configuration_file_path, mock_exists, mock_load_configuration_properties_from_yaml_file, mock_ensure_properties_are_valid):

        mock_determine_configuration_file_path.return_value = 'path-to-configuration-file'
        mock_exists.return_value = True

        load_configuration_file()

        mock_exists.assert_called_with('path-to-configuration-file')

    @patch('config_rpm_maker.config._ensure_properties_are_valid')
    @patch('config_rpm_maker.config._load_configuration_properties_from_yaml_file')
    @patch('config_rpm_maker.config.exists')
    @patch('config_rpm_maker.config._determine_configuration_file_path')
    def test_load_configuration_file_if_it_exists(self, mock_determine_configuration_file_path, mock_exists, mock_load_configuration_properties_from_yaml_file, mock_ensure_properties_are_valid):

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


class SetValueTests(TestCase):

    def test_should_raise_configuration_exception_when_trying_to_set_value_without_name(self):

        self.assertRaises(ConfigException, set_property, name=None, value='123')

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

    def test_get_log_level_should_return_debug_log_level_if_lower_debug_is_given(self):

        actual = _ensure_valid_log_level("debug")

        self.assertEqual(DEBUG, actual)

    def test_get_log_level_should_return_debug_log_level_if_name_contains_whitespace(self):

        actual = _ensure_valid_log_level("\tdeBug    ")

        self.assertEqual(DEBUG, actual)

    def test_get_log_level_should_return_debug_log_level(self):

        actual = _ensure_valid_log_level("DEBUG")

        self.assertEqual(DEBUG, actual)

    def test_get_log_level_should_return_error_log_level(self):

        actual = _ensure_valid_log_level("ERROR")

        self.assertEqual(ERROR, actual)

    def test_get_log_level_should_return_info_log_level(self):

        actual = _ensure_valid_log_level("INFO")

        self.assertEqual(INFO, actual)

    def test_get_log_level_should_raise_exception_when_strange_log_level_given(self):

        self.assertRaises(ConfigException, _ensure_valid_log_level, "FOO")


class GetConfigViewerHostDirTests(TestCase):

    @patch('config_rpm_maker.config.get')
    def test_should_return_path_to_host_directory(self, mock_get):

        mock_get.return_value = 'path-to-config-viewer-host-directory'

        actual_path = build_config_viewer_host_directory_by_hostname('devweb01')

        mock_get.assert_called_with(KEY_CONFIG_VIEWER_HOSTS_DIR)
        self.assertEqual('path-to-config-viewer-host-directory/devweb01', actual_path)

    @patch('config_rpm_maker.config.get')
    def test_should_return_path_and_append_a_postfix(self, mock_get):

        mock_get.return_value = 'path-to-config-viewer-host-directory'

        actual_path = build_config_viewer_host_directory_by_hostname('devweb01', revision='123')

        mock_get.assert_called_with(KEY_CONFIG_VIEWER_HOSTS_DIR)
        self.assertEqual('path-to-config-viewer-host-directory/devweb01.new-revision-123', actual_path)

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

import yaml

from os import environ, getcwd
from os.path import abspath, exists, join
from logging import DEBUG, ERROR, INFO, getLogger
from re import compile

from config_rpm_maker.exceptions import BaseConfigRpmMakerException

LOGGER = getLogger(__name__)


MISSING_CONFIGURATION_FILE_MESSAGE = """Could not find configuration file "{configuration_file_path}"!

Please provide "{default_path}" in the current working directory "{current_working_directory}"
or set environment variable "{environment_variable_name}" to the path where to find the configuration file."""

ENVIRONMENT_VARIABLE_KEY_CONFIGURATION_FILE = 'YADT_CONFIG_RPM_MAKER_CONFIG_FILE'

CONFIGURATION_FILE_PATH = 'yadt-config-rpm-maker.yaml'
DATE_FORMAT = "%d.%m.%Y %H:%M:%S"
LOG_FILE_FORMAT = "%(asctime)s %(levelname)s: %(message)s"
LOG_FILE_DATE_FORMAT = DATE_FORMAT


_properties = None
_file_path_of_loaded_configuration = None


class ConfigurationException(BaseConfigRpmMakerException):
    error_info = "Configuration Error:\n"


class ConfigurationProperty(object):

    def __init__(self, key, default, validator=None):
        self.key = key
        self.default = default
        self.validator = validator

    def __call__(self):
        """ Get the configuration property """

        if not get_properties():
            try:
                load_configuration_file()
            except Exception as e:
                raise e

        properties = get_properties()

        if self not in properties:
            raise ConfigurationException('Requested unknown configuration property "%s"' % self.key)

        return properties[self]


from config_rpm_maker.configuration.properties import *


def load_configuration_file():
    """
        Determines where the configuration file to load might be,
        loads it and ensures the loaded properties are valid.
    """
    configuration_file_path = _determine_configuration_file_path()

    if not exists(configuration_file_path):
        message = MISSING_CONFIGURATION_FILE_MESSAGE.format(configuration_file_path=configuration_file_path,
                                                            default_path=CONFIGURATION_FILE_PATH,
                                                            current_working_directory=abspath('.'),
                                                            environment_variable_name=ENVIRONMENT_VARIABLE_KEY_CONFIGURATION_FILE)
        raise ConfigurationException(message)

    raw_properties = _load_configuration_properties_from_yaml_file(configuration_file_path)
    valid_properties = _ensure_properties_are_valid(raw_properties)
    set_properties(valid_properties)


def build_config_viewer_host_directory(hostname, revision=False):
    """ Returns a path to the config viewer host directory"""
    config_viewer_hosts_directory = get_config_viewer_host_directory()
    path = join(config_viewer_hosts_directory, hostname)

    if revision:
        path += ".new-revision-" + revision

    return path


def set_property(name, value):
    """
        set the configuration property identied by the given name to the given value.

        Before setting the property it will check if the configuration file has already been loaded.
        If this is not the case it will load the configuration file.
    """
    if not name:
        raise ConfigurationException("No configuration property name given")

    configuration = get_properties()

    if not configuration:
        load_configuration_file()
        configuration = get_properties()

    configuration[name] = value


def get_properties():
    """ Returns the application configuration properties if they have already been loaded"""
    return _properties


def set_properties(new_properties):
    """ Sets the application configuration properties (a dictionary) """
    global _properties
    _properties = new_properties


def get_file_path_of_loaded_configuration():
    """ Returns the path to the loaded configuration file (if it has been loaded) """
    return _file_path_of_loaded_configuration


def _set_file_path_of_loaded_configuration(new_file_path):
    """ Use this function after load a configuration file to declare which file has been loaded """
    global _file_path_of_loaded_configuration
    _file_path_of_loaded_configuration = new_file_path


def _determine_configuration_file_path():
    """
        Decides which configuration file to load and returns the path to the file.

        It will try to read the environment variable and
        if this is not available it will fall back to the default file path.
    """
    return environ.get(ENVIRONMENT_VARIABLE_KEY_CONFIGURATION_FILE, CONFIGURATION_FILE_PATH)


def _load_configuration_properties_from_yaml_file(configuration_file_path):
    """ Load the configuration properties from the given path to a yaml file. """
    try:
        with open(configuration_file_path) as configuration_file:
            properties = yaml.load(configuration_file)
            _set_file_path_of_loaded_configuration(configuration_file_path)
            return properties

    except Exception as e:
        error_message = 'Could not load configuration file "%s".\nCurrent working directory is "%s"\nError: %s' % (configuration_file_path, getcwd(), str(e))
        raise ConfigurationException(error_message)


def _ensure_properties_are_valid(raw_properties):
    """
        Ensures that the configuration properties are valid by parsing them.
        If there is a default defined for a property it will return the default value.

        Returns a dictionary containing valid application configuration properties.
        Throws a exception if some parameters are invalid.
    """
    if raw_properties is None:
        LOGGER.warn("Loaded configuration properties are empty.")
        raw_properties = {}

    allow_unknown_hosts = raw_properties.get(unknown_hosts_are_allowed.key, unknown_hosts_are_allowed.default)
    config_rpm_prefix = raw_properties.get(get_config_rpm_prefix.key, get_config_rpm_prefix.default)
    config_viewer_hosts_dir = raw_properties.get(get_config_viewer_host_directory.key, get_config_viewer_host_directory.default)
    custom_dns_searchlist = raw_properties.get(get_custom_dns_search_list.key, get_custom_dns_search_list.default)
    error_log_directory = raw_properties.get(get_error_log_directory.key, get_error_log_directory.default)
    error_log_url = raw_properties.get(get_error_log_url.key, get_error_log_url.default)
    log_level = raw_properties.get(get_log_level.key, get_log_level.default)
    max_file_size = raw_properties.get(get_max_file_size.key, get_max_file_size.default)
    max_failed_hosts = raw_properties.get(get_max_failed_hosts.key, get_max_failed_hosts.default)
    path_to_spec_file = raw_properties.get(get_path_to_spec_file.key, get_path_to_spec_file.default)
    repo_packages_regex = raw_properties.get(get_repo_packages_regex.key, get_repo_packages_regex.default)
    rpm_upload_chunk_size = raw_properties.get(get_rpm_upload_chunk_size.key, get_rpm_upload_chunk_size.default)
    rpm_upload_command = raw_properties.get(get_rpm_upload_command.key, get_rpm_upload_command.default)
    svn_path_to_config = raw_properties.get(get_svn_path_to_config.key, get_svn_path_to_config.default)
    temporary_directory = raw_properties.get(get_temporary_directory.key, get_temporary_directory.default)
    thread_count = raw_properties.get(get_thread_count.key, get_thread_count.default)

    valid_properties = {
        get_log_level: _ensure_valid_log_level(log_level),
        unknown_hosts_are_allowed: _ensure_is_a_boolean_value(unknown_hosts_are_allowed, allow_unknown_hosts),
        get_config_rpm_prefix: _ensure_is_a_string(get_config_rpm_prefix, config_rpm_prefix),
        is_config_viewer_only_enabled: is_config_viewer_only_enabled.default,
        get_config_viewer_host_directory: _ensure_is_a_string(get_config_viewer_host_directory, config_viewer_hosts_dir),
        get_custom_dns_search_list: _ensure_is_a_list_of_strings(get_custom_dns_search_list, custom_dns_searchlist),
        get_error_log_directory: _ensure_is_a_string(get_error_log_directory, error_log_directory),
        get_error_log_url: _ensure_is_a_string(get_error_log_url, error_log_url),
        get_max_failed_hosts: _ensure_is_an_integer(get_max_failed_hosts, max_failed_hosts),
        get_max_file_size: _ensure_is_an_integer(get_max_file_size, max_file_size),
        is_no_clean_up_enabled: is_no_clean_up_enabled.default,
        get_path_to_spec_file: _ensure_is_a_string(get_path_to_spec_file, path_to_spec_file),
        get_repo_packages_regex: _ensure_repo_packages_regex_is_a_valid_regular_expression(repo_packages_regex),
        get_rpm_upload_chunk_size: _ensure_is_an_integer(get_rpm_upload_chunk_size, rpm_upload_chunk_size),
        get_rpm_upload_command: _ensure_is_a_string_or_none(get_rpm_upload_command, rpm_upload_command),
        get_svn_path_to_config: _ensure_is_a_string(get_svn_path_to_config, svn_path_to_config),
        get_thread_count: _ensure_is_an_integer(get_thread_count, thread_count),
        get_temporary_directory: _ensure_is_a_string(get_temporary_directory, temporary_directory),
        is_verbose_enabled: is_verbose_enabled.default
    }

    valid_property_keys = set(map(lambda configuration_property: configuration_property.key, valid_properties.keys()))
    unknown_configuration_properties = set(raw_properties.keys()) - valid_property_keys

    if len(unknown_configuration_properties) > 0:
        LOGGER.warn('Unknown configuration propertie(s) found: %s' % ', '.join(unknown_configuration_properties))

    return valid_properties


def _ensure_is_a_boolean_value(key, value):
    """ Returns a boolean value or raises a exception if the given value is not a boolean """

    if type(value) is not bool:
        raise ConfigurationException('Invalid value "%s" for "%s" has to be a boolean.' % (value, key))

    return value


def _ensure_valid_log_level(log_level_name):
    """ Returns a valid log level """

    if type(log_level_name) is not str:
        raise ConfigurationException('Invalid log level "%s". Log level has to be a string (DEBUG, ERROR or INFO).' % str(log_level_name))

    log_level_name = log_level_name.upper().strip()

    if log_level_name == 'DEBUG':
        return DEBUG
    elif log_level_name == 'INFO':
        return INFO
    elif log_level_name == 'ERROR':
        return ERROR

    raise ConfigurationException('Invalid log level "%s". Log level hast to be DEBUG, ERROR or INFO' % log_level_name)


def _ensure_is_a_string(key, value):
    """ Retuns the given string """

    value_type = type(value)
    if value_type is not str:
        raise ConfigurationException('Configuration parameter "%s": invalid value "%s" of type "%s"! Please use a string.'
                                     % (key, str(value), value_type.__name__))

    return value


def _ensure_is_an_integer(key, value):
    """ Returns the given int """

    value_type = type(value)
    if value_type is not int:
        raise ConfigurationException('Configuration parameter "%s": invalid value "%s" of type "%s"! Please use an integer.'
                                     % (key, str(value), value_type.__name__))

    return value


def _ensure_repo_packages_regex_is_a_valid_regular_expression(value):

    value_type = type(value)
    if value_type is not str:
        raise ConfigurationException('Configuration parameter "%s": invalid value "%s" of type "%s"! The parameter has to be a valid regular expression.'
                                     % (get_repo_packages_regex, str(value), value_type.__name__))

    try:
        compile(value)
    except Exception as e:
        raise ConfigurationException('The given string "%s" is not a valid regular expression. Error was "%s".' % (value, str(e)))

    return value


def _ensure_is_a_string_or_none(key, value):

    if value is None:
        return None

    value_type = type(value)
    if value_type is not str:
        raise ConfigurationException('Configuration parameter "%s": invalid value "%s" of type "%s"! Please use a string.'
                                     % (key, str(value), value_type.__name__))

    return value


def _ensure_is_a_list_of_strings(key, value):

    value_type = type(value)
    if value_type is not list:
        raise ConfigurationException('Configuration parameter "%s": invalid value "%s" of type "%s"! Please use a list of strings.'
                                     % (key, str(value), value_type.__name__))

    for element in value:
        element_type = type(element)
        if element_type is not str:
            raise ConfigurationException('Configuration parameter "%s": invalid list "%s"  with element "%s" of type "%s"! Please use a list of strings.'
                                         % (key, str(value), str(element), element_type.__name__))

    return value

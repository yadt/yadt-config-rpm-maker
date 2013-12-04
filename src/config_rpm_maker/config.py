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

DEFAULT_ALLOW_UNKNOWN_HOSTS = True
DEFAULT_CONFIG_VIEWER_DIR = '/tmp'
DEFAULT_CONFIG_VIEWER_ONLY = False
DEFAULT_CONFIG_RPM_PREFIX = 'yadt-config-'
DEFAULT_CUSTOM_DNS_SEARCHLIST = []
DEFAULT_CONFIGURATION_FILE_PATH = 'yadt-config-rpm-maker.yaml'
DEFAULT_DATE_FORMAT = "%d.%m.%Y %H:%M:%S"
DEFAULT_ERROR_LOG_URL = ''
DEFAULT_ERROR_LOG_DIRECTORY = ""
DEFAULT_MAX_FILE_SIZE = 100 * 1024
DEFAULT_HOST_NAME_ENCODING = 'ascii'
DEFAULT_LOG_FORMAT = "[%(levelname)5s] %(message)s"
DEFAULT_LOG_LEVEL = 'DEBUG'
DEFAULT_PATH_TO_SPEC_FILE = 'default.spec'
DEFAULT_REPO_PACKAGES_REGEX = '.*-repo.*'
DEFAULT_RPM_UPLOAD_CHUNK_SIZE = 10
DEFAULT_RPM_UPLOAD_COMMAND = None
DEFAULT_SVN_PATH_TO_CONFIG = '/config'
DEFAULT_SYS_LOG_ADDRESS = "/dev/log"
DEFAULT_SYS_LOG_FORMAT = "config_rpm_maker[{0}]: [%(levelname)5s] %(message)s"
DEFAULT_SYS_LOG_LEVEL = DEBUG
DEFAULT_THREAD_COUNT = 1
DEFAULT_TEMP_DIR = '/tmp'
DEFAULT_UPLOAD_CHUNK_SIZE = 0

ENVIRONMENT_VARIABLE_KEY_CONFIGURATION_FILE = 'YADT_CONFIG_RPM_MAKER_CONFIG_FILE'
ENVIRONMENT_VARIABLE_KEY_KEEP_WORKING_DIRECTORY = 'KEEPWORKDIR'

KEY_ALLOW_UNKNOWN_HOSTS = 'allow_unknown_hosts'
KEY_CONFIG_VIEWER_ONLY = 'config_viewer_only'
KEY_CONFIG_VIEWER_HOSTS_DIR = 'config_viewer_hosts_dir'
KEY_CONFIG_RPM_PREFIX = 'config_rpm_prefix'
KEY_CUSTOM_DNS_SEARCHLIST = 'custom_dns_searchlist'
KEY_ERROR_LOG_DIRECTORY = 'error_log_dir'
KEY_ERROR_LOG_URL = 'error_log_url'
KEY_LOG_FORMAT = "log_format"
KEY_LOG_LEVEL = "log_level"
KEY_PATH_TO_SPEC_FILE = 'path_to_spec_file'
KEY_RPM_UPLOAD_CHUNK_SIZE = 'rpm_upload_chunk_size'
KEY_RPM_UPLOAD_COMMAND = 'rpm_upload_cmd'
KEY_REPO_PACKAGES_REGEX = 'repo_packages_regex'
KEY_SVN_PATH_TO_CONFIG = 'svn_path_to_config'
KEY_SVN_PATH_TO_CONFIGURATION = 'svn_path_to_config'
KEY_TEMPORARY_DIRECTORY = "temp_dir"
KEY_THREAD_COUNT = 'thread_count'
KEY_TEMP_DIR = 'temp_dir'
KEY_MAX_FILE_SIZE = 'max_file_size'
LOG_FILE_FORMAT = "%(asctime)s %(levelname)s: %(message)s"
LOG_FILE_DATE_FORMAT = DEFAULT_DATE_FORMAT


_properties = None
_file_path_of_loaded_configuration = None


class ConfigException(BaseConfigRpmMakerException):
    error_info = "Configuration Error:\n"


class ConfigurationValidationException(ConfigException):
    error_info = "Invalid configuration:\n"


def load_configuration_file():
    """
        Determines where the configuration file to load might be,
        loads it and ensures the loaded properties are valid.
    """
    configuration_file_path = _determine_configuration_file_path()

    if not exists(configuration_file_path):
        raise ConfigException("""Could not find configuration file "%s". Please provide "%s" in the current working directory "%s" or set environment variable "%s".""" %
                              (DEFAULT_CONFIGURATION_FILE_PATH,
                               configuration_file_path,
                               abspath('.'),
                               ENVIRONMENT_VARIABLE_KEY_CONFIGURATION_FILE))

    raw_properties = _load_configuration_properties_from_yaml_file(configuration_file_path)
    valid_properties = _ensure_properties_are_valid(raw_properties)
    set_properties(valid_properties)


def get(name):
    """ Get the configuration property """

    if not get_properties():
        try:
            load_configuration_file()
        except Exception as e:
            raise e

    properties = get_properties()

    if name not in properties:
        raise ConfigException('Requested unknown configuration property "%s"' % name)

    return properties[name]


def build_config_viewer_host_directory(hostname, revision=False):
    """ Returns a path to the config viewer host directory"""
    config_viewer_hosts_directory = get(KEY_CONFIG_VIEWER_HOSTS_DIR)
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
        raise ConfigException("No configuration property name given")

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
    return environ.get(ENVIRONMENT_VARIABLE_KEY_CONFIGURATION_FILE, DEFAULT_CONFIGURATION_FILE_PATH)


def _load_configuration_properties_from_yaml_file(configuration_file_path):
    """ Load the configuration properties from the given path to a yaml file. """
    try:
        with open(configuration_file_path) as configuration_file:
            properties = yaml.load(configuration_file)
            _set_file_path_of_loaded_configuration(configuration_file_path)
            return properties

    except Exception as e:
        error_message = 'Could not load configuration file "%s".\nCurrent working directory is "%s"\nError: %s' % (configuration_file_path, getcwd(), str(e))
        raise ConfigException(error_message)


def _ensure_properties_are_valid(raw_properties):
    """
        Ensures that the configuration properties are valid by parsing them.
        If there is a default defined for a property it will return the default value.

        Returns a dictionary containing valid application configuration properties.
        Throws a exception if some parameters are invalid.
    """
    if raw_properties is None:
        raise ConfigurationValidationException("Loaded configuration properties are empty.")

    allow_unknown_hosts = raw_properties.get(KEY_ALLOW_UNKNOWN_HOSTS, DEFAULT_ALLOW_UNKNOWN_HOSTS)
    config_rpm_prefix = raw_properties.get(KEY_CONFIG_RPM_PREFIX, DEFAULT_CONFIG_RPM_PREFIX)
    config_viewer_hosts_dir = raw_properties.get(KEY_CONFIG_VIEWER_HOSTS_DIR, DEFAULT_CONFIG_VIEWER_DIR)
    custom_dns_searchlist = raw_properties.get(KEY_CUSTOM_DNS_SEARCHLIST, DEFAULT_CUSTOM_DNS_SEARCHLIST)
    error_log_directory = raw_properties.get(KEY_ERROR_LOG_DIRECTORY, DEFAULT_ERROR_LOG_DIRECTORY)
    error_log_url = raw_properties.get(KEY_ERROR_LOG_URL, DEFAULT_ERROR_LOG_URL)
    log_level = raw_properties.get(KEY_LOG_LEVEL, DEFAULT_LOG_LEVEL)
    max_file_size = raw_properties.get(KEY_MAX_FILE_SIZE, DEFAULT_MAX_FILE_SIZE)
    path_to_spec_file = raw_properties.get(KEY_PATH_TO_SPEC_FILE, DEFAULT_PATH_TO_SPEC_FILE)
    repo_packages_regex = raw_properties.get(KEY_REPO_PACKAGES_REGEX, DEFAULT_REPO_PACKAGES_REGEX)
    rpm_upload_chunk_size = raw_properties.get(KEY_RPM_UPLOAD_CHUNK_SIZE, DEFAULT_RPM_UPLOAD_CHUNK_SIZE)
    rpm_upload_command = raw_properties.get(KEY_RPM_UPLOAD_COMMAND, DEFAULT_RPM_UPLOAD_COMMAND)
    svn_path_to_config = raw_properties.get(KEY_SVN_PATH_TO_CONFIG, DEFAULT_SVN_PATH_TO_CONFIG)
    temporary_directory = raw_properties.get(KEY_TEMP_DIR, DEFAULT_TEMP_DIR)
    thread_count = raw_properties.get(KEY_THREAD_COUNT, DEFAULT_THREAD_COUNT)

    valid_properties = {
        KEY_LOG_LEVEL: _ensure_valid_log_level(log_level),
        KEY_ALLOW_UNKNOWN_HOSTS: _ensure_is_a_boolean_value(KEY_ALLOW_UNKNOWN_HOSTS, allow_unknown_hosts),
        KEY_CONFIG_RPM_PREFIX: _ensure_is_a_string(KEY_CONFIG_RPM_PREFIX, config_rpm_prefix),
        KEY_CONFIG_VIEWER_ONLY: DEFAULT_CONFIG_VIEWER_ONLY,
        KEY_CONFIG_VIEWER_HOSTS_DIR: _ensure_is_a_string(KEY_CONFIG_VIEWER_HOSTS_DIR, config_viewer_hosts_dir),
        KEY_CUSTOM_DNS_SEARCHLIST: _ensure_is_a_list_of_strings(KEY_CUSTOM_DNS_SEARCHLIST, custom_dns_searchlist),
        KEY_ERROR_LOG_DIRECTORY: _ensure_is_a_string(KEY_ERROR_LOG_DIRECTORY, error_log_directory),
        KEY_ERROR_LOG_URL: _ensure_is_a_string(KEY_ERROR_LOG_URL, error_log_url),
        KEY_MAX_FILE_SIZE: _ensure_is_an_integer(KEY_MAX_FILE_SIZE, max_file_size),
        KEY_PATH_TO_SPEC_FILE: _ensure_is_a_string(KEY_PATH_TO_SPEC_FILE, path_to_spec_file),
        KEY_REPO_PACKAGES_REGEX: _ensure_repo_packages_regex_is_a_valid_regular_expression(repo_packages_regex),
        KEY_RPM_UPLOAD_CHUNK_SIZE: _ensure_is_an_integer(KEY_RPM_UPLOAD_CHUNK_SIZE, rpm_upload_chunk_size),
        KEY_RPM_UPLOAD_COMMAND: _ensure_is_a_string_or_none(KEY_RPM_UPLOAD_COMMAND, rpm_upload_command),
        KEY_SVN_PATH_TO_CONFIG: _ensure_is_a_string(KEY_SVN_PATH_TO_CONFIGURATION, svn_path_to_config),
        KEY_THREAD_COUNT: _ensure_is_an_integer(KEY_THREAD_COUNT, thread_count),
        KEY_TEMP_DIR: _ensure_is_a_string(KEY_TEMP_DIR, temporary_directory)
    }

    unknown_configuration_parameters = set(raw_properties.keys()) - set(valid_properties.keys())

    if len(unknown_configuration_parameters) > 0:
        raise ConfigException('Unknown configuration parameter(s) found: %s' % ', '.join(unknown_configuration_parameters))

    return valid_properties


def _ensure_is_a_boolean_value(key, value):
    """ Returns a boolean value or raises a exception if the given value is not a boolean """

    if type(value) is not bool:
        raise ConfigException('Invalid value "%s" for "%s" has to be a boolean.' % (value, key))

    return value


def _ensure_valid_log_level(log_level_name):
    """ Returns a valid log level """

    if type(log_level_name) is not str:
        raise ConfigException('Invalid log level "%s". Log level has to be a string (DEBUG, ERROR or INFO).' % str(log_level_name))

    log_level_name = log_level_name.upper().strip()

    if log_level_name == 'DEBUG':
        return DEBUG
    elif log_level_name == 'INFO':
        return INFO
    elif log_level_name == 'ERROR':
        return ERROR

    raise ConfigException('Invalid log level "%s". Log level hast to be DEBUG, ERROR or INFO' % log_level_name)


def _ensure_is_a_string(key, value):
    """ Retuns the given string """

    value_type = type(value)
    if value_type is not str:
        raise ConfigException('Configuration parameter "%s": invalid value "%s" of type "%s"! Please use a string.'
                              % (key, str(value), value_type.__name__))

    return value


def _ensure_is_an_integer(key, value):
    """ Returns the given int """

    value_type = type(value)
    if value_type is not int:
        raise ConfigException('Configuration parameter "%s": invalid value "%s" of type "%s"! Please use an integer.'
                              % (key, str(value), value_type.__name__))

    return value


def _ensure_repo_packages_regex_is_a_valid_regular_expression(value):

    value_type = type(value)
    if value_type is not str:
        raise ConfigException('Configuration parameter "%s": invalid value "%s" of type "%s"! Please use a string which is a valid regex.'
                              % (KEY_REPO_PACKAGES_REGEX, str(value), value_type.__name__))

    try:
        compile(value)
    except Exception as e:
        raise ConfigException('The given string "%s" is not a valid regular expression. Error was "%s".' % (value, str(e)))

    return value


def _ensure_is_a_string_or_none(key, value):

    if value is None:
        return None

    value_type = type(value)
    if value_type is not str:
        raise ConfigException('Configuration parameter "%s": invalid value "%s" of type "%s"! Please use a string.'
                              % (key, str(value), value_type.__name__))

    return value


def _ensure_is_a_list_of_strings(key, value):

    value_type = type(value)
    if value_type is not list:
        raise ConfigException('Configuration parameter "%s": invalid value "%s" of type "%s"! Please use a list of strings.'
                              % (key, str(value), value_type.__name__))

    for element in value:
        element_type = type(element)
        if element_type is not str:
            raise ConfigException('Configuration parameter "%s": invalid list "%s"  with element "%s" of type "%s"! Please use a list of strings.'
                                  % (key, str(value), str(element), element_type.__name__))

    return value

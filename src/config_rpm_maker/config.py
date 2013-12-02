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
DEFAULT_FILE_SIZE_MAXIMUM = 100 * 1024
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
KEY_ERROR_URL_DIRECTORY = 'error_log_url'
KEY_LOG_FORMAT = "log_format"
KEY_LOG_LEVEL = "log_level"
KEY_RPM_UPLOAD_COMMAND = 'rpm_upload_cmd'
KEY_SVN_PATH_TO_CONFIG = 'svn_path_to_config'
KEY_TEMPORARY_DIRECTORY = "temp_dir"
KEY_THREAD_COUNT = 'thread_count'
KEY_PATH_TO_SPEC_FILE = 'path_to_spec_file'
KEY_REPO_PACKAGES_REGEX = 'repo_packages_regex'
KEY_RPM_UPLOAD_CHUNK_SIZE = 'rpm_upload_chunk_size'
KEY_SVN_PATH_TO_CONFIGURATION = 'svn_path_to_config'
KEY_THREAD_COUNT = 'thread_count'
KEY_TEMP_DIR = 'temp_dir'
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


def get(name, default=None):
    """ Get the configuration property """
    if not _properties:
        try:
            load_configuration_file()
        except Exception as e:
            if default:
                return default
            else:
                raise e

    if name in _properties:
        return _properties[name]
    else:
        return default


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

    valid_properties = {
        KEY_LOG_LEVEL: _ensure_valid_log_level(raw_properties.get(KEY_LOG_LEVEL, DEFAULT_LOG_LEVEL)),
        KEY_ALLOW_UNKNOWN_HOSTS: _ensure_valid_allow_unknown_hosts(raw_properties.get(KEY_ALLOW_UNKNOWN_HOSTS, DEFAULT_ALLOW_UNKNOWN_HOSTS)),
        KEY_CONFIG_RPM_PREFIX: raw_properties.get(KEY_CONFIG_RPM_PREFIX, DEFAULT_CONFIG_RPM_PREFIX),
        KEY_CONFIG_VIEWER_HOSTS_DIR: raw_properties.get(KEY_CONFIG_VIEWER_HOSTS_DIR, DEFAULT_CONFIG_VIEWER_DIR),
        KEY_CUSTOM_DNS_SEARCHLIST: raw_properties.get(KEY_CUSTOM_DNS_SEARCHLIST, DEFAULT_CUSTOM_DNS_SEARCHLIST),
        KEY_ERROR_LOG_DIRECTORY: raw_properties.get(KEY_ERROR_LOG_DIRECTORY, DEFAULT_ERROR_LOG_DIRECTORY),
        KEY_ERROR_URL_DIRECTORY: raw_properties.get(KEY_ERROR_URL_DIRECTORY, DEFAULT_ERROR_LOG_URL),
        KEY_PATH_TO_SPEC_FILE: raw_properties.get(KEY_PATH_TO_SPEC_FILE, DEFAULT_PATH_TO_SPEC_FILE),
        KEY_REPO_PACKAGES_REGEX: raw_properties.get(KEY_REPO_PACKAGES_REGEX, DEFAULT_REPO_PACKAGES_REGEX),
        KEY_RPM_UPLOAD_CHUNK_SIZE: raw_properties.get(KEY_RPM_UPLOAD_CHUNK_SIZE, DEFAULT_RPM_UPLOAD_CHUNK_SIZE),
        KEY_RPM_UPLOAD_COMMAND: raw_properties.get(KEY_RPM_UPLOAD_COMMAND, DEFAULT_RPM_UPLOAD_COMMAND),
        KEY_SVN_PATH_TO_CONFIG: raw_properties.get(KEY_SVN_PATH_TO_CONFIG, DEFAULT_SVN_PATH_TO_CONFIG),
        KEY_THREAD_COUNT: raw_properties.get(KEY_THREAD_COUNT, DEFAULT_THREAD_COUNT),
        KEY_TEMP_DIR: raw_properties.get(KEY_TEMP_DIR, DEFAULT_TEMP_DIR)
    }

    return valid_properties


def _ensure_valid_allow_unknown_hosts(allow_unknown_hosts):
    """ Returns a valid value for allow unknown hosts """
    if type(allow_unknown_hosts) is not bool:
        raise ConfigException('Invalid value "%s" for "%s" has to be a boolean.' % (allow_unknown_hosts, KEY_ALLOW_UNKNOWN_HOSTS))

    return allow_unknown_hosts


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

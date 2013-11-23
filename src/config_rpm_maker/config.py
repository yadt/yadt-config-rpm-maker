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

import os
import yaml

from logging import DEBUG, ERROR, INFO, getLogger

from config_rpm_maker.exceptions import BaseConfigRpmMakerException

LOGGER = getLogger(__name__)

DEFAULT_CONFIG_VIEWER_ONLY = False
DEFAULT_CONFIGURATION_FILE_PATH = 'yadt-config-rpm-maker.yaml'
DEFAULT_DATE_FORMAT = "%d.%m.%Y %H:%M:%S"
DEFAULT_ERROR_LOG_URL = ''
DEFAULT_FILE_SIZE_MAXIMUM = 100 * 1024
DEFAULT_HOST_NAME_ENCODING = 'ascii'
DEFAULT_LOG_FORMAT = "[%(levelname)5s] %(message)s"
DEFAULT_LOG_LEVEL = INFO
DEFAULT_RPM_UPLOAD_CMD = False
DEFAULT_SYS_LOG_ADDRESS = "/dev/log"
DEFAULT_SYS_LOG_FORMAT = "config_rpm_maker[{0}]: [%(levelname)5s] %(message)s"
DEFAULT_SYS_LOG_LEVEL = DEBUG
DEFAULT_THREAD_COUNT = 1
DEFAULT_UPLOAD_CHUNK_SIZE = 0

KEY_CONFIG_VIEWER_ONLY = 'config_viewer_only'
KEY_LOG_FORMAT = "log_format"
KEY_LOG_LEVEL = "log_level"
KEY_RPM_UPLOAD_CMD = 'rpm_upload_cmd'
KEY_SVN_PATH_TO_CONFIG = 'svn_path_to_config'
KEY_TEMPORARY_DIRECTORY = "temp_dir"
KEY_THREAD_COUNT = 'thread_count'

LOG_FILE_FORMAT = "%(asctime)s %(levelname)s: %(message)s"
LOG_FILE_DATE_FORMAT = DEFAULT_DATE_FORMAT


configuration = None
configuration_file_path = DEFAULT_CONFIGURATION_FILE_PATH


class ConfigException(BaseConfigRpmMakerException):
    error_info = "Configuration Error:\n"


def get_temporary_directory():
    """ Returns the temporary directory """

    return get(KEY_TEMPORARY_DIRECTORY)


def get_log_level():
    """ Returns configured log level or default log level """

    log_level_name = get(KEY_LOG_LEVEL, DEFAULT_LOG_LEVEL)

    if log_level_name == 'DEBUG':
        return DEBUG
    elif log_level_name == 'INFO':
        return INFO
    elif log_level_name == 'ERROR':
        return ERROR

    raise ConfigException('Invalid log level "%s". Log level hast to be DEBUG, ERROR or INFO' % log_level_name)


def load_configuration_file():
    global configuration, configuration_file_path
    configuration_file_path = os.environ.get('YADT_CONFIG_RPM_MAKER_CONFIG_FILE', configuration_file_path)
    if os.path.exists(configuration_file_path):
        try:
            with open(configuration_file_path) as f:
                configuration = yaml.load(f)

        except Exception as e:
            raise ConfigException('Could not load configuration file "%s".\nError: %s' % (configuration_file_path, str(e)))
    else:
        raise ConfigException("Could not find configuration file '%s'. Please provide a 'yadt-config-rpm-maker.yaml' in the current working directory '%s' or set environment variable 'YADT_CONFIG_RPM_MAKER_CONFIG_FILE'." % (configuration_file_path, os.path.abspath('.')))


def get(name, default=None):
    if not configuration:
        try:
            load_configuration_file()
        except Exception as e:
            if default:
                return default
            else:
                raise e

    if name in configuration:
        return configuration[name]
    else:
        return default


def setvalue(name, value):
    if not name:
        raise Exception("No name given")

    if not configuration:
        load_configuration_file()

    configuration[name] = value

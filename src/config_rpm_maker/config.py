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

from logging import getLogger

from config_rpm_maker.exceptions import BaseConfigRpmMakerException

LOGGER = getLogger("config_rpm_maker.config")

DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)5s [%(name)s] - %(message)s"

KEY_LOG_FORMAT = "log_format"
KEY_LOG_LEVEL = "log_level"
KEY_TEMPORARY_DIRECTORY = "temp_dir"

__config = None


class ConfigException(BaseConfigRpmMakerException):
    error_info = "Configuration Error:\n"


def get_temporary_directory():
    """ Returns the temporary directory """

    get(KEY_TEMPORARY_DIRECTORY)


def __init_config():
    global __config
    config_file_path = os.environ.get('YADT_CONFIG_RPM_MAKER_CONFIG_FILE', 'yadt-config-rpm-maker.yaml')
    if os.path.exists(config_file_path):
        try:
            LOGGER.info('Loading configration file "%s"', config_file_path)
            with open(config_file_path) as f:
                __config = yaml.load(f)

            LOGGER.debug('Configuration %s', str(__config))
        except Exception as e:
            raise ConfigException("Could not load config file '%s'" % config_file_path, e)
    else:
        raise ConfigException("Could not find config file '%s'. Please provide a 'yadt-config-rpm-maker.yaml' in the current working directory '%s' or set environment variable 'YADT_CONFIG_RPM_MAKER_CONFIG_FILE'." % (config_file_path, os.path.abspath('.')))


def get(name, default=None):
    if not __config:
        try:
            __init_config()
        except Exception as e:
            if default:
                return default
            else:
                raise e

    if name in __config:
        return __config[name]
    else:
        return default


def setvalue(name, value):
    if not name:
        raise Exception("No name given")

    if not __config:
        __init_config()

    __config[name] = value

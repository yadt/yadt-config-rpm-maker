import logging
import os
import yaml
from config_rpm_maker.exceptions import BaseConfigRpmMakerException

__config = None


class ConfigException(BaseConfigRpmMakerException):
    error_info = "Configuration Error:\n"


def __init_config():
    global __config
    config_file_path = os.environ.get('YADT_CONFIG_RPM_MAKER_CONFIG_FILE', 'yadt-config-rpm-maker.yaml')
    if os.path.exists(config_file_path):
        try:
            with open(config_file_path) as f:
                __config = yaml.load(f)

            logging.debug("Loaded config file '%s' config: %s", config_file_path, str(__config))
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

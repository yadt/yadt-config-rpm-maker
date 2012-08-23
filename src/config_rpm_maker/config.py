import logging
import os
import yaml

config = {}

config_file_path = os.environ.get('YADT_CONFIG_RPM_MAKER_CONFIG_FILE', 'yadt-config-rpm-maker.yaml')
if os.path.exists(config_file_path):
    try:
        with open(config_file_path) as f:
            config = yaml.load(f)

        logging.info("Loaded config file '%s' config: %s", config_file_path, str(config))
    except Exception as e:
        raise Exception("Could not load config file '%s'" % config_file_path, e)
else:
    raise Exception("Could not find config file '%s'. Please provide a 'yadt-config-rpm-maker.yaml' in the current working directory '%s' or set environment variable 'YADT_CONFIG_RPM_MAKER_CONFIG_FILE'." % (config_file_path, os.path.abspath('.')))

def get(name, default = None):
    if config.has_key(name):
        return config[name]
    else:
        return default
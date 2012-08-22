import logging
import os
import yaml

config = {}

config_file_path = os.environ.get('YADT_CONFIG_RPM_MAKER_CONFIG_FILE', '/etc/yadt-config-rpm-maker.yaml')
if os.path.exists(config_file_path):
    with open(config_file_path) as f:
        config = yaml.load(f)

    logging.info("Loaded config file '%s' config: %s", config_file_path, str(config))

def get(name, default = None):
    if config.has_key(name):
        return config[name]
    else:
        return default
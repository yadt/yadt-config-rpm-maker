import logging
import os
import yaml

config = {}

if os.environ.has_key('YADT_CONFIG_RPM_MAKER_CONFIG_FILE') and os.path.exists(os.environ['YADT_CONFIG_RPM_MAKER_CONFIG_FILE']):
    path = os.environ['YADT_CONFIG_RPM_MAKER_CONFIG_FILE']
    f = open(path)
    try:
        config = yaml.load(f)
        logging.info("Loaded config file '%s' config: %s", path, str(config))
    finally:
        f.close()

def get(name, default = None):
    if config.has_key(name):
        return config[name]
    else:
        return default
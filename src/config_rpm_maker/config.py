import os
import yaml

config = {}

if os.environ.has_key('YADT_CONFIG_RPM_MAKER_CONFIG_FILE') and os.path.exists(os.environ['YADT_CONFIG_RPM_MAKER_CONFIG_FILE']):
    f = open(os.environ['YADT_CONFIG_RPM_MAKER_CONFIG_FILE'])
    try:
        config = yaml.load(f)
    finally:
        f.close()

def get(name, default = None):
    if config.has_key(name):
        return config[name]
    else:
        return default
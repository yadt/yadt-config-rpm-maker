import os
import yaml

config = {}

if os.environ.has_key('TEST_CONFIG_FILE') and os.path.exists(os.environ['TEST_CONFIG_FILE']):
    f = open(os.environ['TEST_CONFIG_FILE'])
    try:
        config = yaml.load(f)
    finally:
        f.close()

def get(name):
    return config[name]
import logging
import os
import yaml

__config = None

def __init_config():
    global __config
    config_file_path = os.environ.get('YADT_CONFIG_RPM_MAKER_CONFIG_FILE', 'yadt-config-rpm-maker.yaml')
    if os.path.exists(config_file_path):
        try:
            with open(config_file_path) as f:
                __config = yaml.load(f)
    
            logging.debug("Loaded config file '%s' config: %s", config_file_path, str(__config))
        except Exception as e:
            raise Exception("Could not load config file '%s'" % config_file_path, e)
    else:
        raise Exception("Could not find config file '%s'. Please provide a 'yadt-config-rpm-maker.yaml' in the current working directory '%s' or set environment variable 'YADT_CONFIG_RPM_MAKER_CONFIG_FILE'." % (config_file_path, os.path.abspath('.')))

def get(name, default = None):
    if not __config:
        try:
            __init_config()
        except Exception as e:
            if default:
                return default
            else:
                raise e
                
        
    if __config.has_key(name):
        return __config[name]
    else:
        return default
    
def setvalue(name,value):
    if not name:
        raise Exception("No name given")
    
    if not __config:
        __init_config()
    
    __config[name] = value
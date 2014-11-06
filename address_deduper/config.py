import logging

from address_normalizer.deduping.storage.base import *

valid_configs = {}

MB = 1024 * 1024

class ConfigMeta(type):
    def __init__(cls, name, bases, dict_):
        if name != 'BaseConfig':
            assert hasattr(cls, 'env'), 'Config class %s has no attribute "env"' % name
            valid_configs[cls.env] = cls
        super(ConfigMeta, cls).__init__(name, bases, dict_)


class BaseConfig(object):
    __metaclass__ = ConfigMeta
    
    DEBUG = True

    TEST = False
    
    LOG_LEVEL = logging.INFO
    LOG_DIR = '.'
    
    MAX_LOG_BYTES = 10 * MB
    LOG_BACKUPS = 3
    LOG_ROLLOVER_INTERVAL = 'midnight'

    STORAGE = storage_types.LEVELDB

    STORAGE_LEVELDB_DIR = '/tmp/dupes'
    CLEAN_DB_ON_START = True

    CLIENT_ONLY = False
    
class DevConfig(BaseConfig):
    env = 'dev'

current_env = DevConfig.env

def current_config():
    return valid_configs[current_env]

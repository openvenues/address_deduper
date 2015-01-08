import logging
import os

from address_normalizer.deduping.storage.base import *

valid_configs = {}

MB = 1024 * 1024

APP_NAME = 'DEDUPER'

class ConfigMeta(type):
    def __init__(cls, name, bases, dict_):
        if name != 'BaseConfig':
            assert hasattr(cls, 'env'), 'Config class %s has no attribute "env"' % name
            valid_configs[cls.env] = cls
        else:
            '''For environment variables, specify DEDUPER_{VAR_NAME}={VALUE}
            The prefix is to avoid conflicts with existing environment variables.
            N.B. This only works with string config variables like paths, etc. Can
            also specify DEDUPER_STORAGE={LEVELDB|ROCKSDB}'''
            for name in dict_.iterkeys():
                if not name.startswith('_'):
                    env_var = os.environ.get(u'_'.join([APP_NAME, name]), None)
                    if env_var is not None:
                        setattr(cls, name, env_var)

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

    '''
    Number of characters of the geohash to use in deduping for lat/longs
    Higher = more precise, lower = more forgiving
    Geohashes has the property that if two hashes share a common prefix of at least n characters, they are within a certain distance of each other
    The prefix width can be thought of as a bounding box with a width and a height defining what is considered "nearby". For the distance table, see: http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/search-aggregations-bucket-geohashgrid-aggregation.html
    Since we use the 8 neighbor tiles as well (to avoid missing locations that are close to each other simply because they are across a faultline), multiply those numbers by 3 to cover the full 9-tile span for which lat/longs can match
    '''
    GEOHASH_PRECISION = 5

    STORAGE = storage_types.LEVELDB

    STORAGE_LEVELDB_DIR = '/tmp/dupes'
    CLEAN_DB_ON_START = True

    CLIENT_ONLY = False
    
class DevConfig(BaseConfig):
    env = 'dev'

current_env = DevConfig.env

def current_config():
    return valid_configs[current_env]

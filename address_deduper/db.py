import os
import shutil

from address_normalizer.deduping.storage.base import *

def db_from_config(config):
    storage_type = config.get('STORAGE', storage_types.NOP)

    if storage_type == storage_types.NOP:
        return NopStorage()
    elif storage_type == storage_types.LEVELDB:
        import address_normalizer.deduping.storage.level as level
        db_dir = config['STORAGE_LEVELDB_DIR']
        if config.get('CLEAN_DB_ON_START', False) and os.path.exists(db_dir):
            shutil.rmtree(db_dir)
        else:
            os.unlink(os.path.join(db_dir, 'LOCK'))

        return level.LevelDBNearDupeStorage(level.LevelDB(db_dir))
    elif storage_type == storage_types.ROCKSDB:
        import address_normalizer.deduping.storage.rocks as rocks
        db_dir = config['STORAGE_ROCKSDB_DIR']
        if config.get('CLEAN_DB_ON_START', False) and os.path.exists(db_dir):
            shutil.rmtree(db_dir)
        else:
            os.unlink(os.path.join(db_dir, 'LOCK'))
        return rocks.RocksDBNearDupeStorage(rocks.RocksDB(db_dir))

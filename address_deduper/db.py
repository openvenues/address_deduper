import os
import shutil

from address_normalizer.deduping.storage.base import *

def cleanup_db_dir(db_dir, config):
    if config.get('CLEAN_DB_ON_START', False) and os.path.exists(db_dir):
        shutil.rmtree(db_dir)
    else:
        lock_path = os.path.join(db_dir, 'LOCK')
        if os.path.exists(lock_path):
            os.unlink(lock_path)

def db_from_config(config):
    storage_type = config.get('STORAGE', storage_types.NOP)
    if isinstance(storage_type, basestring):
        storage_type = storage_types.from_string(storage_type)

    if storage_type == storage_types.NOP:
        return NopStorage()
    elif storage_type == storage_types.LEVELDB:
        import address_normalizer.deduping.storage.level as level
        db_dir = config['STORAGE_LEVELDB_DIR']
        cleanup_db_dir(db_dir, config)
        return level.LevelDBNearDupeStorage(level.LevelDB(db_dir))
    elif storage_type == storage_types.ROCKSDB:
        import address_normalizer.deduping.storage.rocks as rocks
        import rocksdb
        db_dir = config['STORAGE_ROCKSDB_DIR']
        cleanup_db_dir(db_dir, config)
        return rocks.RocksDBNearDupeStorage(rocksdb.RocksDB(db_dir, rocksdb.Options(create_if_missing=True)))

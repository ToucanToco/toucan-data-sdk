import io
import logging
import os
import shutil
import zipfile

import pandas as pd


logger = logging.getLogger(__name__)


class ToucanDataSdk:
    EXTRACTION_CACHE_PATH = 'extraction_cache'
    EXTRACTION_CACHE_PATH_BK = 'extraction_cache.bk'

    def __init__(self, client):
        self.client = client
        self._dfs = None

    @property
    def dfs(self):
        if self._dfs is None:
            if os.path.exists(self.EXTRACTION_CACHE_PATH):
                self._dfs = self.read_cache()
                logger.info('DataFrames extracted from cache')
            else:
                resp = self.client.sdk.get()
                dfs = self.cache_dfs(resp.content)
                self._dfs = dfs
                logger.info('Data fetched and cached')
        return self._dfs

    def cache_dfs(self, dfs_zip):
        """
        Args:
            dfs_zip (zipfile.ZipFile):

        Returns:
            dict: Dict[str, DataFrame]
        """
        if not os.path.exists(self.EXTRACTION_CACHE_PATH):
            os.makedirs(self.EXTRACTION_CACHE_PATH)

        with io.BytesIO(dfs_zip) as bio:
            with zipfile.ZipFile(bio, mode='r') as z_file:
                names = z_file.namelist()
                for name in names:
                    data = z_file.read(name)
                    self._write_entry(name, data)
                return {
                    name: self._read_entry(name) for name in names
                }

    def read_cache(self):
        """
        Returns:
            dict: Dict[str, DataFrame]
        """
        logger.info(
            'Reading data from cache ({})'.format(self.EXTRACTION_CACHE_PATH))
        return {
            name: self._read_entry(name)
            for name in os.listdir(self.EXTRACTION_CACHE_PATH)
        }

    def invalidate_cache(self):
        self._dfs = None
        self.backup_existing_cache()

    def backup_existing_cache(self):
        if os.path.exists(self.EXTRACTION_CACHE_PATH):
            if os.path.exists(self.EXTRACTION_CACHE_PATH_BK):
                try:
                    shutil.rmtree(self.EXTRACTION_CACHE_PATH_BK)
                except (OSError, IOError) as e:  # For Python 2.7+ compatibility
                    logger.error('failed to remove old backup: ' + str(e))
                    return

            try:
                os.rename(self.EXTRACTION_CACHE_PATH, self.EXTRACTION_CACHE_PATH_BK)
            except (OSError, IOError) as e:
                logger.error('failed to backup current cache' + str(e))

    def _write_entry(self, file_name, data):
        """
        Args:
            file_name (str):
            data (bytes):
        """
        file_path = os.path.join(self.EXTRACTION_CACHE_PATH, file_name)
        with open(file_path, mode='wb') as f:
            f.write(data)
        logger.info('Cache entry added: {}'.format(file_path))

    def _read_entry(self, file_name):
        """
        Args:
            file_name (str):

        Returns:
            DataFrame:
        """
        file_path = os.path.join(self.EXTRACTION_CACHE_PATH, file_name)

        logger.info('Reading cache entry: {}'.format(file_path))
        return pd.read_feather(file_path)

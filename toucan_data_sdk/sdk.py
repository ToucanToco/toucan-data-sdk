import logging
import os
import shutil
import tempfile
import zipfile

import joblib
from toucan_client import ToucanClient


logger = logging.getLogger(__name__)


class ToucanDataSdk:
    EXTRACTION_CACHE_PATH = 'extraction_cache'
    EXTRACTION_CACHE_PATH_BK = 'extraction_cache.bk'

    def __init__(self, small_app_url, auth, stage="staging"):
        self.client = ToucanClient(small_app_url, auth=auth)
        self.client.stage = stage
        self._dfs = None

    @property
    def dfs(self):
        if self._dfs is None:
            if self.cache_exists():
                self._dfs = self.read()
                logger.info('DataFrames extracted from cache')
            else:
                resp = self.client.sdk.post()
                resp.raise_for_status()
                self._dfs = self.write(resp.content)
                logger.info('Data fetched and cached')
        return self._dfs

    def invalidate_cache(self):
        self._dfs = None
        self.backup_cache()

    def read(self):
        """
        Returns:
            dict: Dict[str, DataFrame]
        """
        logger.info(
            'Reading data from cache ({})'.format(self.EXTRACTION_CACHE_PATH))
        return {
            name: self.read_entry(name)
            for name in os.listdir(self.EXTRACTION_CACHE_PATH)
        }

    def read_entry(self, file_name):
        """
        Args:
            file_name (str):

        Returns:
            pd.DataFrame:
        """
        file_path = os.path.join(self.EXTRACTION_CACHE_PATH, file_name)
        logger.info('Reading cache entry: {}'.format(file_path))
        return joblib.load(file_path)

    def write(self, data):
        """
        Args:
            data (str | byte):

        Returns:
            dict: Dict[str, DataFrame]
        """
        if not os.path.exists(self.EXTRACTION_CACHE_PATH):
            os.makedirs(self.EXTRACTION_CACHE_PATH)

        dfs = extract(data)
        for name, df in dfs.items():
            self.write_entry(name, df)
        return dfs

    def write_entry(self, file_name, df):
        """
        Args:
            file_name (str):
            df (DataFrame):
        """
        file_path = os.path.join(self.EXTRACTION_CACHE_PATH, file_name)
        joblib.dump(df, filename=file_path)
        logger.info('Cache entry added: {}'.format(file_path))

    def cache_exists(self):
        return os.path.exists(self.EXTRACTION_CACHE_PATH) and \
            os.path.isdir(self.EXTRACTION_CACHE_PATH)

    def backup_cache(self):
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


def extract_zip(tmp_file):
    """
    Returns:
        dict: Dict[str, DataFrame]
    """
    dfs = {}
    with zipfile.ZipFile(tmp_file.name, mode='r') as z_file:
        names = z_file.namelist()
        for name in names:
            content = z_file.read(name)
            with tempfile.NamedTemporaryFile() as tmp_file:
                tmp_file.write(content)
                tmp_file.flush()
                tmp_file.seek(0)
                dfs[name] = joblib.load(tmp_file.name)
    return dfs


def extract(data):
    """
    Args:
        data (str | byte):

    Returns:
        dict: Dict[str, DataFrame]

    """
    with tempfile.NamedTemporaryFile() as tmp_file:
        tmp_file.write(data)
        tmp_file.flush()
        tmp_file.seek(0)

        if is_zipfile(tmp_file):
            return extract_zip(tmp_file)
        else:
            raise DataSdkError('Unsupported file type')


def is_zipfile(tmp_file):
    """
    Args:
        tmp_file (tempfile.TemporaryFile):

    Returns:
        bool:
    """
    try:
        return zipfile.is_zipfile(tmp_file.name)
    except Exception:
        return False
    finally:
        tmp_file.seek(0)


class DataSdkError(Exception):
    pass

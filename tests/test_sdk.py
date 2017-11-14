import shutil
from collections import namedtuple
from unittest.mock import MagicMock

import os
import pytest

from toucan_data_sdk.sdk import ToucanDataSdk


@pytest.fixture(name='client', scope='function')
def gen_client():
    resp = namedtuple('Response', ['content'])(content=1)
    client = MagicMock()
    client.sdk.get.return_value = resp
    return client


@pytest.fixture(name='sdk', scope='function')
def gen_data_sdk(client):
    yield ToucanDataSdk(client)
    if os.path.exists(ToucanDataSdk.EXTRACTION_CACHE_PATH):
        shutil.rmtree(ToucanDataSdk.EXTRACTION_CACHE_PATH)


def test_dfs(sdk, mocker):
    """It should use the cache properly"""
    # 1. Cache directory exists
    mock_path_exists = mocker.patch('os.path.exists')
    mock_read_cache = mocker.patch(
        'toucan_data_sdk.sdk.ToucanDataSdk.read_cache')
    mock_cache_dfs = mocker.patch(
        'toucan_data_sdk.sdk.ToucanDataSdk.cache_dfs')

    mock_path_exists.return_value = True
    mock_read_cache.return_value = 1
    assert sdk.dfs == 1

    # 2. Invalidate cache, disable cache
    mock_path_exists.return_value = False
    mock_cache_dfs.return_value = 2
    sdk._dfs = None
    assert sdk.dfs == 2

    # 3. Do not invalidate cache, keep last value
    mock_path_exists.return_value = False
    mock_cache_dfs.return_value = 3
    assert sdk.dfs == 2

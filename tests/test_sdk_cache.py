import copy
import shutil
from collections import namedtuple
from unittest.mock import MagicMock

import os
import pandas as pd
import pytest

from tests.utils import default_zip_file
from toucan_client.client import SmallAppRequester

from toucan_data_sdk import ToucanDataSdk

DF = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
DF2 = pd.DataFrame({'a': ['a', 'b'], 'b': ['c', 'd']})
ZIP_CONTENT = default_zip_file(DF, DF2)
BASE_ROUTE = 'fake.route/my-small-app'


@pytest.fixture(name='client', scope='function')
def gen_client():
    resp = namedtuple('Response', ['content'])(content=copy.copy(ZIP_CONTENT))
    client = MagicMock()
    client.sdk.get = MagicMock(return_value=resp)
    return client


@pytest.fixture(name='sdk', scope='function')
def gen_data_sdk(client):
    yield ToucanDataSdk(client)
    if os.path.exists(ToucanDataSdk.EXTRACTION_CACHE_PATH):
        shutil.rmtree(ToucanDataSdk.EXTRACTION_CACHE_PATH)


def test_cache(sdk):
    # Cache is empty -> fill it
    dfs = sdk.dfs
    assert sdk.client.sdk.get.call_count == 1
    assert isinstance(dfs, dict)
    assert 'df' in dfs
    assert 'df2' in dfs

    assert DF.equals(dfs['df'])
    assert DF2.equals(dfs['df2'])

    # Cache is filled, no request to the server should been made
    sdk.client.sdk.get.reset_mock()
    _ = sdk.dfs
    sdk.client.sdk.get.assert_not_called()

    assert isinstance(dfs, dict)
    assert 'df' in dfs
    assert 'df2' in dfs

    assert DF.equals(dfs['df'])
    assert DF2.equals(dfs['df2'])


def test_invalidate_cache(sdk):
    # Cache is empty -> fill it
    dfs = sdk.dfs
    assert sdk.client.sdk.get.call_count == 1
    assert isinstance(dfs, dict)
    assert 'df' in dfs
    assert 'df2' in dfs

    assert DF.equals(dfs['df'])
    assert DF2.equals(dfs['df2'])

    # Invalidate cache
    sdk.invalidate_cache()

    dfs = sdk.dfs
    assert sdk.client.sdk.get.call_count == 1
    assert isinstance(dfs, dict)
    assert 'df' in dfs
    assert 'df2' in dfs

    assert DF.equals(dfs['df'])
    assert DF2.equals(dfs['df2'])


def test_backup_existing_cache(sdk, mocker):
    mock_path_exists = mocker.patch('os.path.exists')
    mock_rmtree = mocker.patch('shutil.rmtree')
    mock_rename = mocker.patch('os.rename')

    # 1. No cache, nothing to do
    mock_path_exists.return_value = False
    sdk.backup_existing_cache()

    assert mock_path_exists.call_count == 1
    assert mock_rmtree.call_count == 0
    assert mock_rename.call_count == 0

    mock_path_exists.reset_mock()

    # 2. Cache exists and previous backup exists
    mock_path_exists.return_value = True
    sdk.backup_existing_cache()

    assert mock_path_exists.call_count == 2
    assert mock_rmtree.call_count == 1
    assert mock_rename.call_count == 1

    mock_path_exists.reset_mock()
    mock_rmtree.reset_mock()
    mock_rename.reset_mock()

    # 3.1 Cache exists and previous backup exists, errors
    mock_path_exists.return_value = True
    mock_rmtree.side_effect = IOError('rmtree failed')
    sdk.backup_existing_cache()

    assert mock_path_exists.call_count == 2
    assert mock_rmtree.call_count == 1
    assert mock_rename.call_count == 0

    mock_path_exists.reset_mock()
    mock_rmtree.reset_mock()
    mock_rename.reset_mock()

    # 3.2 Cache exists and previous backup exists, errors
    mock_path_exists.side_effect = [True, False]
    mock_rename.side_effect = IOError('rename failed')
    sdk.backup_existing_cache()

    assert mock_path_exists.call_count == 2
    assert mock_rmtree.call_count == 0
    assert mock_rename.call_count == 1

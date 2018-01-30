import os
import shutil
import tempfile

import joblib
import pytest
from requests import HTTPError

from tests.tools import DF, DF2
from toucan_data_sdk.sdk import ToucanDataSdk


def gen_client(mocker):
    class Response:
        content = 10

        def raise_for_status(self):
            pass

    resp = Response()
    client = mocker.MagicMock()
    client.sdk.post.return_value = resp
    return client


@pytest.fixture(name='sdk', scope='function')
def gen_data_sdk(mocker):
    sdk = ToucanDataSdk('some_url', auth=('', ''))
    sdk.client = gen_client(mocker)
    yield sdk
    if os.path.exists(ToucanDataSdk.EXTRACTION_CACHE_PATH):
        shutil.rmtree(ToucanDataSdk.EXTRACTION_CACHE_PATH)


def gen_client_error(mocker):
    class Response:
        content = 10

        def raise_for_status(self):
            raise HTTPError()

    resp = Response()
    client = mocker.MagicMock()
    client.sdk.post.return_value = resp
    return client


@pytest.fixture(name='sdk_error', scope='function')
def gen_data_sdk_error(mocker):
    sdk = ToucanDataSdk('some_url', auth=('', ''))
    sdk.client = gen_client_error(mocker)
    yield sdk
    if os.path.exists(ToucanDataSdk.EXTRACTION_CACHE_PATH):
        shutil.rmtree(ToucanDataSdk.EXTRACTION_CACHE_PATH)


@pytest.fixture(name='tmp_dir', scope='module')
def gen_tmp_dir():
    return tempfile.gettempdir()


@pytest.fixture(name='tmp_file', scope='function')
def gen_tmp_file(tmp_dir):
    tmp_file = tempfile.NamedTemporaryFile(dir=tmp_dir)
    yield tmp_file
    tmp_file.close()


@pytest.fixture(name='tmp_file2', scope='function')
def gen_tmp_file2(tmp_dir):
    tmp_file = tempfile.NamedTemporaryFile(dir=tmp_dir)
    yield tmp_file
    tmp_file.close()


def test_dfs(sdk, mocker):
    """It should use the cache properly"""
    mock_cache_exists = mocker.patch(
        'toucan_data_sdk.sdk.ToucanDataSdk.cache_exists')
    mock_read = mocker.patch(
        'toucan_data_sdk.sdk.ToucanDataSdk.read')
    mock_write = mocker.patch(
        'toucan_data_sdk.sdk.ToucanDataSdk.write')

    # 1. Cache directory exists
    mock_cache_exists.return_value = True
    mock_read.return_value = 1
    assert sdk.dfs == 1

    # 2. Cache directory does not exist
    mock_cache_exists.return_value = False
    mock_write.return_value = 2
    sdk._dfs = None
    assert sdk.dfs == 2

    # 3. Cache directory does not exist, keep last set value
    mock_cache_exists.return_value = False
    mock_write.return_value = 3
    assert sdk.dfs == 2


def test_dfs_http_error(sdk_error):
    """It should use the cache properly"""
    with pytest.raises(HTTPError):
        _ = sdk_error.dfs


def test_read(sdk):
    with tempfile.TemporaryDirectory() as tmp_dir:
        extraction_dir = os.path.join(tmp_dir, sdk.EXTRACTION_CACHE_PATH)
        sdk.EXTRACTION_CACHE_PATH = extraction_dir
        os.makedirs(extraction_dir)

        joblib.dump(DF, os.path.join(extraction_dir, 'a'))
        joblib.dump(DF2, os.path.join(extraction_dir, 'b'))

        dfs = sdk.read()
        assert 'a' in dfs
        assert 'b' in dfs
        assert DF.equals(dfs['a'])
        assert DF2.equals(dfs['b'])


def test_write(sdk, mocker):
    mock_extract = mocker.patch('toucan_data_sdk.sdk.extract')
    mock_extract.return_value = {'a': DF, 'b': DF2}

    with tempfile.TemporaryDirectory() as tmp_dir:
        extraction_dir = os.path.join(tmp_dir, sdk.EXTRACTION_CACHE_PATH)
        sdk.EXTRACTION_CACHE_PATH = extraction_dir

        sdk.write({'a': DF, 'b': DF2})

        assert os.path.exists(extraction_dir)
        assert 'a' in os.listdir(extraction_dir)
        assert 'b' in os.listdir(extraction_dir)


def test_cache(sdk, mocker):
    mock_read = mocker.patch('toucan_data_sdk.sdk.ToucanDataSdk.read')
    mock_write = mocker.patch('toucan_data_sdk.sdk.ToucanDataSdk.write')
    mock_path_exists = mocker.patch('os.path.exists')
    mock_is_dir = mocker.patch('os.path.isdir')

    # Cache is empty -> fill it
    mock_path_exists.return_value = False
    mock_write.return_value = {'df': DF, 'df2': DF2}

    dfs = sdk.dfs
    assert sdk.client.sdk.post.call_count == 1
    assert isinstance(dfs, dict)
    assert 'df' in dfs
    assert 'df2' in dfs

    assert DF.equals(dfs['df'])
    assert DF2.equals(dfs['df2'])

    # Cache is filled, no request to the server
    mock_path_exists.return_value = True
    mock_is_dir.return_value = True
    mock_read.return_value = {'df': DF, 'df2': DF2}

    sdk.client.sdk.post.reset_mock()
    _ = sdk.dfs
    sdk.client.sdk.post.assert_not_called()

    assert isinstance(dfs, dict)
    assert 'df' in dfs
    assert 'df2' in dfs

    assert DF.equals(dfs['df'])
    assert DF2.equals(dfs['df2'])

    mocker.stopall()


def test_invalidate_cache(sdk, mocker):
    mock_write = mocker.patch('toucan_data_sdk.sdk.ToucanDataSdk.write')
    mock_write.return_value = {'df': DF, 'df2': DF2}

    # Cache is empty -> fill it
    dfs = sdk.dfs
    assert sdk.client.sdk.post.call_count == 1
    assert isinstance(dfs, dict)
    assert 'df' in dfs
    assert 'df2' in dfs

    assert DF.equals(dfs['df'])
    assert DF2.equals(dfs['df2'])

    # Invalidate cache
    sdk.invalidate_cache()
    sdk.client.sdk.post.reset_mock()

    dfs = sdk.dfs
    assert sdk.client.sdk.post.call_count == 1
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
    sdk.backup_cache()

    assert mock_path_exists.call_count == 1
    assert mock_rmtree.call_count == 0
    assert mock_rename.call_count == 0

    mock_path_exists.reset_mock()

    # 2. Cache exists and previous backup exists
    mock_path_exists.return_value = True
    sdk.backup_cache()

    assert mock_path_exists.call_count == 2
    assert mock_rmtree.call_count == 1
    assert mock_rename.call_count == 1

    mock_path_exists.reset_mock()
    mock_rmtree.reset_mock()
    mock_rename.reset_mock()

    # 3.1 Cache exists and previous backup exists, error
    mock_path_exists.return_value = True
    mock_rmtree.side_effect = IOError('rmtree failed')
    sdk.backup_cache()

    assert mock_path_exists.call_count == 2
    assert mock_rmtree.call_count == 1
    assert mock_rename.call_count == 0

    mock_path_exists.reset_mock()
    mock_rmtree.reset_mock()
    mock_rename.reset_mock()

    # 3.2 Cache exists and previous backup exists, other error
    mock_path_exists.side_effect = [True, False]
    mock_rename.side_effect = IOError('rename failed')
    sdk.backup_cache()

    assert mock_path_exists.call_count == 2
    assert mock_rmtree.call_count == 0
    assert mock_rename.call_count == 1

    mocker.stopall()

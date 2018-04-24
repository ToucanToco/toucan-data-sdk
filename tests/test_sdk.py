import os
import shutil
import tempfile

import joblib
import pytest
from requests import HTTPError

from tests.tools import DF, DF2
from toucan_data_sdk.sdk import ToucanDataSdk, InvalidQueryError


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
    sdk = ToucanDataSdk(
        instance_url='https://api-myinstance.toucantoco.com',
        small_app='demo',
        auth=('', '')
    )
    sdk.client = gen_client(mocker)
    yield sdk
    if os.path.exists(sdk.EXTRACTION_CACHE_PATH):
        shutil.rmtree(sdk.EXTRACTION_CACHE_PATH)


@pytest.fixture(name='sdk_old', scope='function')
def gen_data_sdk_old(mocker):
    sdk_old = ToucanDataSdk(
        instance_url='https://api-myinstance.toucantoco.com/demo',
        auth=('', '')
    )
    sdk_old.client = gen_client(mocker)
    yield sdk_old
    if os.path.exists(sdk_old.EXTRACTION_CACHE_PATH):
        shutil.rmtree(sdk_old.EXTRACTION_CACHE_PATH)


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
    sdk = ToucanDataSdk('some_url', small_app='demo', auth=('', ''))
    sdk.client = gen_client_error(mocker)
    yield sdk
    if os.path.exists(sdk.EXTRACTION_CACHE_PATH):
        shutil.rmtree(sdk.EXTRACTION_CACHE_PATH)


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
    mock_read_cache = mocker.patch(
        'toucan_data_sdk.sdk.ToucanDataSdk.read_from_cache')
    mock_read_sdk = mocker.patch(
        'toucan_data_sdk.sdk.ToucanDataSdk.read_from_sdk')

    # 1. Cache directory exists
    mock_cache_exists.return_value = True
    mock_read_cache.return_value = {"domain_1": 1}
    assert sdk.get_dfs() == {"domain_1": 1}

    # 2. Cache directory does not exist
    mock_read_cache.reset_mock()
    mock_cache_exists.return_value = False
    mock_read_sdk.return_value = {"domain_2": 1}
    assert sdk.get_dfs() == {"domain_2": 1}
    mock_read_cache.assert_not_called()

    # 3. Cache directory exists with one domain
    mock_cache_exists.return_value = True
    mock_read_cache.return_value = {"domain_1": 1}
    assert sdk.get_dfs(['a']) == {"domain_1": 1}

    # 4. Cache directory doesn't exists with one domain
    mock_read_cache.reset_mock()
    mock_cache_exists.return_value = False
    mock_read_sdk.return_value = {"domain_2": 1}
    assert sdk.get_dfs(['a']) == {"domain_2": 1}
    mock_read_cache.assert_not_called()
    assert sdk.small_app_url == 'https://api-myinstance.toucantoco.com/demo'


def test_dfs_complex(sdk, mocker):
    """It should use the cache properly"""
    mock_cache_exists = mocker.patch(
        'toucan_data_sdk.sdk.ToucanDataSdk.cache_exists')
    mock_read_cache = mocker.patch(
        'toucan_data_sdk.sdk.ToucanDataSdk.read_from_cache')
    mock_read_sdk = mocker.patch(
        'toucan_data_sdk.sdk.ToucanDataSdk.read_from_sdk')

    mock_cache_exists.side_effect = [True, False]
    mock_read_cache.return_value = {"domain_1": 1}
    mock_read_sdk.return_value = {"domain_2": 1}
    assert sdk.get_dfs(['a', 'b']) == {"domain_1": 1, "domain_2": 1}


def test_dfs_http_error(sdk_error):
    """It should use the cache properly"""
    with pytest.raises(HTTPError):
        _ = sdk_error.get_dfs()


def test_read_from_cache(sdk):
    with tempfile.TemporaryDirectory() as tmp_dir:
        extraction_dir = os.path.join(tmp_dir, sdk.EXTRACTION_CACHE_PATH)
        sdk.EXTRACTION_CACHE_PATH = extraction_dir
        os.makedirs(extraction_dir)

        joblib.dump(DF, os.path.join(extraction_dir, 'a'))
        joblib.dump(DF2, os.path.join(extraction_dir, 'b'))

        dfs = sdk.read_from_cache()
        assert 'a' in dfs
        assert 'b' in dfs
        assert DF.equals(dfs['a'])
        assert DF2.equals(dfs['b'])

        dfs = sdk.read_from_cache(['a'])
        assert 'a' in dfs
        assert 'b' not in dfs
        assert DF.equals(dfs['a'])


def test_read_from_sdk(sdk, mocker):
    mock_write = mocker.patch('toucan_data_sdk.sdk.ToucanDataSdk.write')
    mock_write.return_value = {'df': DF, 'df2': DF2}
    dfs = sdk.read_from_sdk()
    assert dfs == {'df': DF, 'df2': DF2}


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


def test_invalidate_cache(sdk):
    with tempfile.TemporaryDirectory() as tmp_dir:
        extraction_dir = os.path.join(tmp_dir, sdk.EXTRACTION_CACHE_PATH)
        sdk.EXTRACTION_CACHE_PATH = extraction_dir
        os.makedirs(extraction_dir)
        joblib.dump(DF, os.path.join(extraction_dir, 'a'))
        joblib.dump(DF2, os.path.join(extraction_dir, 'b'))

        assert sdk.cache_exists()
        sdk.invalidate_cache()
        assert not sdk.cache_exists()

        os.makedirs(extraction_dir)
        joblib.dump(DF, os.path.join(extraction_dir, 'a'))
        joblib.dump(DF2, os.path.join(extraction_dir, 'b'))

        assert sdk.cache_exists('a')
        sdk.invalidate_cache(['a'])
        assert not sdk.cache_exists('a')
        assert sdk.cache_exists('b')
        assert sdk.cache_exists()


def test_invalidate_cache_exception(sdk):
    with tempfile.TemporaryDirectory() as tmp_dir:
        sdk.invalidate_cache()

        extraction_dir = os.path.join(tmp_dir, sdk.EXTRACTION_CACHE_PATH)
        sdk.EXTRACTION_CACHE_PATH = extraction_dir
        os.makedirs(extraction_dir)
        joblib.dump(DF, os.path.join(extraction_dir, 'a'))

        assert sdk.cache_exists()
        sdk.invalidate_cache(['b', 'a'])
        assert not sdk.cache_exists('a')


def test_augment(sdk):
    sdk.client.config.augment.get().text = 'yo'
    assert sdk.get_augment() == 'yo'


def test_etl(sdk):
    sdk.client.config.etl.get().json.return_value = {'yo': 'del'}
    assert sdk.get_etl() == {'yo': 'del'}


def test_basemaps(sdk):
    sdk.client.basemaps.post().json.return_value = {'lala': 'lo'}
    assert sdk.query_basemaps({}) == {'lala': 'lo'}
    with pytest.raises(InvalidQueryError):
        sdk.query_basemaps('yo')


def test_sdk_compatibility(sdk_old, mocker):
    """It should use the cache properly"""
    mock_cache_exists = mocker.patch(
        'toucan_data_sdk.sdk.ToucanDataSdk.cache_exists')
    mock_read_cache = mocker.patch(
        'toucan_data_sdk.sdk.ToucanDataSdk.read_from_cache')
    mock_read_sdk = mocker.patch(
        'toucan_data_sdk.sdk.ToucanDataSdk.read_from_sdk')

    # 1. Cache directory exists
    mock_cache_exists.return_value = True
    mock_read_cache.return_value = {"domain_1": 1}
    assert sdk_old.get_dfs() == {"domain_1": 1}
    assert sdk_old.small_app_url == 'https://api-myinstance.toucantoco.com/demo'

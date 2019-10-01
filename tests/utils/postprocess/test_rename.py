import pandas as pd

from toucan_data_sdk.utils.postprocess import rename


def test_rename():
    """ It should return a translated data dict """
    data = pd.DataFrame([{'hello': 'world'}])
    config = {
        'values': {'world': {'fr': 'monde'}},
        'columns': {'hello': {'fr': 'bonjour'}},
        'locale': 'fr',
    }
    df = rename(data, **config)
    res = [{k: v for k, v in zip(df.columns, row)} for row in df.values]
    assert res == [{'bonjour': 'monde'}]


def test_rename_unknown_locale_with_en():
    """It should fallback on en if locale is not found"""
    data = pd.DataFrame([{'hello': 'world'}])
    config = {
        'values': {'world': {'en': 'WORLD'}},
        'columns': {'hello': {'en': 'HELLO'}},
        'locale': 'fr',
    }
    df = rename(data, **config)
    res = [{k: v for k, v in zip(df.columns, row)} for row in df.values]
    assert res == [{'HELLO': 'WORLD'}]


def test_rename_unknown_locale_without_en():
    """It should fallback on untranslated if locale is not found"""
    data = pd.DataFrame([{'hello': 'world'}])
    config = {
        'values': {'world': {'fr': 'monde'}},
        'columns': {'hello': {'fr': 'bonjour'}},
        'locale': 'it',
    }
    df = rename(data, **config)
    res = [{k: v for k, v in zip(df.columns, row)} for row in df.values]
    assert res == [{'hello': 'world'}]

import pytest
import pandas as pd

from toucan_data_sdk.utils.data_specs import (
        model, tabulate_model, tabulate_data_source, generate_md)


def test_model():
    df = pd.DataFrame([{'a': 1, 'b': 'blah', 'c': '2'}])
    mo = model(df)
    assert mo[0]['col'] == 'a'
    assert mo[1]['first'] == '"blah"'


def test_tabulate_model():
    tb = tabulate_model([{'col': 1}])
    assert tb == '|   col |\n|------:|\n|     1 |'


def test_tabulate_data_source():
    tb = tabulate_data_source({'domain': 'aa', 'file': 'aa.csv', 'sep': ';'})
    assert 'field   | value' in tb


def test_generate_md():
    data_sources = [{'domain': 'aa'}, {'domain': 'bb'}]
    dfs = {'aa': pd.DataFrame([{'a': 1}]), 'bb': pd.DataFrame([{'b': 2}])}
    md = generate_md(data_sources, dfs, ['my header'])
    assert len(md) == 3  # two datasources an one header line

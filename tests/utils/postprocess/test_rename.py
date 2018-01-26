import pandas as pd
from toucan_data_sdk.utils.postprocess import rename


def test_rename():
    """ It should return a translated data dict """
    data = pd.DataFrame([{'hello': 'world'}])
    config = {
        'values': {'world': {'fr': 'monde'}},
        'columns': {'hello': {'fr': 'bonjour'}},
        'locale': 'fr'
    }
    data_translated = [{'bonjour': 'monde'}]
    df = rename(data, **config)
    res = [{k: v for k, v in zip(df.columns, row)} for row in df.values]
    assert res == data_translated

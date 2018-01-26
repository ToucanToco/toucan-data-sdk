import pandas as pd
from toucan_data_sdk.utils.generic import aggregate_for_requesters


def test_aggregate_requesters():
    """
    It should aggregate for requesters without losing NaN values
    """
    df = pd.DataFrame([
        {'year': 2017, 'filter1': 'A', 'filter2': 'C', 'value': 1},
        {'year': 2017, 'filter1': 'A', 'filter2': 'D', 'value': 5},
        {'year': 2017, 'filter1': 'B', 'filter2': pd.np.nan, 'value': 2},
        {'year': 2017, 'filter1': 'B', 'filter2': 'C', 'value': 8},
    ])
    res = aggregate_for_requesters(
        df,
        ['year'],
        {'filter1': 'All 1', 'filter2': 'All 2'},
    )
    mask = (res['filter1'] == 'All 1') & (res['filter2'] == 'All 2')
    assert res[mask]['value'][0] == 16
    mask = (res['filter1'] == 'All 1') & (res['filter2'] == 'C')
    assert res[mask]['value'][0] == 9

    res = aggregate_for_requesters(
        df,
        ['year'],
        {'filter1': 'All 1', 'filter2': 'All 2'},
        'max'
    )
    mask = (res['filter1'] == 'All 1') & (res['filter2'] == 'All 2')
    assert res[mask]['value'][0] == 8
    mask = (res['filter1'] == 'All 1') & (res['filter2'] == 'C')
    assert res[mask]['value'][0] == 8

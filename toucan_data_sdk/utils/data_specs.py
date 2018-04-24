import json
from contextlib import suppress

import pandas as pd
from tabulate import tabulate
TABULATE_CONF = {'headers': 'keys', 'showindex': False, 'tablefmt': 'pipe'}


def model(df: pd.DataFrame) -> list:
    """Generate a 'model' for a dataframe, atm list of cols with additional info"""
    mo = []
    for c, d in zip(df.columns, df.dtypes):
        o = {'col': c, 'dtype': d,
             'unique': df[c].is_unique,
             'nullable': df[c].isnull().any(),
             'first': df[c].iloc[0]}
        with suppress(TypeError):
            o['first'] = json.dumps(o['first'])
        mo.append(o)
    return mo


def tabulate_model(mo: list) -> str:
    return pd.DataFrame(mo).pipe(tabulate, **TABULATE_CONF)


def tabulate_data_source(ds: dict) -> str:
    """Tabulate an entry from etl_config."""
    return pd.DataFrame([ds]).melt(var_name='field').pipe(tabulate, **TABULATE_CONF)


def generate_md(data_sources: list, dfs: dict, header: list = None) -> list:
    """Generate one markdown block for each data_source in etl_config"""
    out = []

    if header:
        out += header

    for ds in data_sources:
        out.append('\n'.join([
            f'## Domain: {ds["domain"]}',
            '### ETL config',
            f'{tabulate_data_source(ds)}',
            '### Columns',
            f'{tabulate_model(model(dfs[ds["domain"]]))}'
        ]))

    return out

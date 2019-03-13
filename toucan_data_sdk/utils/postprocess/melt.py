import pandas as pd
from typing import List


def melt(df, id: List[str], value: List[str], dropna=False):
    """
    Melt the data
    ---
    -  `id` (list): Column(s) to use as identifier variables
    - `value` (list): Column(s) to unpivot
    - `dropna` (optional): dropna in added 'value' column
    """
    df = df[(id + value)]
    df = pd.melt(df, id_vars=id, value_vars=value)
    if dropna:
        df = df.dropna(subset=['value'])

    return df

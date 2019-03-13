from typing import Dict, List


def rename(df, values: Dict[str, Dict] = None, columns: List[str] = None, locale: str = None):
    """
    Replaces data values and column names according to locale
    ---
    - `values`:
        - key: term to be replaced
        - value:
            - key: 'en' or 'fr'
            - value: term's translation
    - `columns`:
        - key: columns name to be replaced
        - value:
            - key: 'en' or 'fr'
            - value: column name's translation
    - `local` (optional: str): 'en' or 'fr'
    """
    if values:
        to_replace = list(values.keys())
        value = [values[term][locale] for term in values]
        df = df.replace(to_replace=to_replace, value=value)
    if columns:
        _keys = list(columns.keys())
        _values = [column[locale] for column in columns.values()]
        columns = dict(list(zip(_keys, _values)))
        df = df.rename(columns=columns)
    return df

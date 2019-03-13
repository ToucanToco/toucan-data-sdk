from typing import List


def sort(df, columns: List[str], order='asc'):
    """
    Sort data
    ---
    - `columns` (list): list of the names of the columns to sort
    - `order` (optional: str): 'asc' (default) or 'desc'
    """
    ascending = order != 'desc'
    return df.sort_values(columns, ascending=ascending)

from typing import List


def drop_duplicates(df, columns: List[str]):
    """
    Drop duplicated rows

    - columns(optional): list of column name to identify duplicates, if 'None' all columns are used
    """
    return df.drop_duplicates(columns)


def query_df(df, query):
    """
    Slice the data according to the provided query

    - query: your query as a string
    pandas documentation:
    http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.query.html#pandas.DataFrame.query
    """
    df = df.query(query)
    return df


query = query_df

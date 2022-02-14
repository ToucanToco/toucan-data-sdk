from typing import TYPE_CHECKING, Dict, List, Optional

from toucan_data_sdk.utils.helpers import slugify

if TYPE_CHECKING:
    import pandas as pd


def get_category_cols(df: "pd.DataFrame", threshold: int) -> List[str]:
    obj_df = df.select_dtypes(include=["object"])
    return [col for col in obj_df.columns if len(obj_df[col].unique()) < threshold]


def get_int_cols(df: "pd.DataFrame") -> List[str]:
    float_df = df.select_dtypes(include=["floating"])
    return [col for col in float_df.columns if all(x.is_integer() for x in float_df[col])]


def clean_dataframe(
    df: "pd.DataFrame",
    is_slugify: bool = True,
    threshold: int = 50,
    rename_cols: Optional[Dict[str, str]] = None,
) -> "pd.DataFrame":
    """
    This method is used to:
    - slugify the column names (if slugify is set to True)
    - convert columns to 'category' (if len(unique) < threshold) or 'int'
    - clean the dataframe and rename if necessary
    """
    if is_slugify:
        df = df.rename(columns=slugify)

    df = df.dropna(axis=1, how="all")
    for column in get_category_cols(df, threshold=threshold):
        df[column] = df[column].astype("category")
    for column in get_int_cols(df):
        df[column] = df[column].astype(int)

    if rename_cols is not None:
        df = df.rename(columns=rename_cols)

    return df

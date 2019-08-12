import pandas as pd
import toucan_data_sdk.utils.generic as generic_functions
import toucan_data_sdk.utils.postprocess as postprocess_functions


def _apply_condition(df, condition, new_column):
    """
    `condition` can be a simple string or integer
    but also a dictionary or a list of dictionaries with postprocesses
    """
    # Single postprocess
    if isinstance(condition, dict):
        condition = [condition]

    # Postprocesses
    if isinstance(condition, list):
        for postprocess_infos in condition:
            postprocess_name = postprocess_infos.pop('postprocess')
            # Retrieve the right postprocess function
            if postprocess_name == 'if_else':
                postprocess_function = if_else
            else:
                postprocess_function = (
                        getattr(postprocess_functions, postprocess_name, None) or
                        getattr(generic_functions, postprocess_name)
                )
            # Apply the postprocess to the dataframe
            if 'new_column' not in postprocess_infos:
                postprocess_infos['new_column'] = new_column
            df = postprocess_function(df, **postprocess_infos)
    else:
        # Simple value: condition is a string or a number
        df[new_column] = condition

    return df


def _if_else(df, *, if_, then_, else_=None, new_column):
    if_sub_df = df.query(if_)
    else_sub_df = df[~df.index.isin(if_sub_df.index)]

    if_sub_df = _apply_condition(if_sub_df, then_, new_column)
    else_sub_df = _apply_condition(else_sub_df, else_, new_column)

    new_df = pd.concat([if_sub_df, else_sub_df]).sort_index()

    # Put back the order in columns
    new_cols = [col for col in new_df.columns if col not in df.columns]
    return new_df[[*df.columns, *new_cols]]


def if_else(df, **kwargs):
    """
    The usual if...then...else... statement

    ---

    ### Parameters

    *mandatory :*
    - `if` (*str*): string representing the query to filter the data (same as the one used in the postprocess 'query')
      See [pandas doc](
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.query.html) for more information
    - `then`:
      - *str, int, float*: A row value to use for the new column
      - *dict or list of dicts*: postprocesses functions to have more logic (see examples)
    - `new_column` (*str*): name of the column containing the result.

    *optional :*
    - `else`: same as then but for the non filtered part.
      If not set, the non filtered part won't have any values for the new column

    ---

    ### Example

    ** Input**

    | country  |    city  | clean | the rating |
    |:--------:|:--------:|:-----:|:----------:|
    | France   |  Paris   |   -1  |      3     |
    | Germany  |  Munich  |    4  |      5     |
    | France   |   Nice   |    3  |      4     |
    |  Hell    | HellCity |   -10 |      0     |

    ```cson
    if_else:
      if: '`the rating` % 2 == 0'
      then:
        postprocess: 'formula'
        formula: '("the rating" + clean) / 2'
      else: 'Hey !'
      new_column: 'new'
    ```

    **Output**

    | country  |    city  | clean | the rating | new  |
    |:--------:|:--------:|:-----:|:----------:|:----:|
    | France   |  Paris   |   -1  |      3     | Hey! |
    | Germany  |  Munich  |    4  |      5     | Hey! |
    | France   |   Nice   |    3  |      4     | 3.5  |
    |  Hell    | HellCity |   -10 |      0     | -5.0 |
    """
    for kw in ('if', 'then', 'else'):
        if kw in kwargs:
            kwargs[f'{kw}_'] = kwargs.pop(kw)
    return _if_else(df, **kwargs)

def replace(df, column: str, new_column: str = None, **kwargs):
    """
    Change the label of a value or a columns within your data source.
    (Similar to `rename` but does not have the notion of locale)

    ---

    ### Parameters

    *mandatory :*
    - `column` (*str*): name of the column to modify.
    - `to_replace` (*dict*): keys of this dict are old values pointing on substitute.

    *optional :*
    - `new_column` (*str*): name of the output column. By default the `column` arguments is modified.

    **Note**: extra parameters can be used (see [pandas doc](
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.replace.html))

    ---

    ### Example

    **Input**

    article | rating
    :------:|:------:
    book    | 1
    puzzle  | 3
    food    | 5

    We want to split the ratings in three categories: "good", "average" and "poor".

    ```cson
    replace:
      column: "rating"
      new_column: "rating_category"  # create a new column with replaced data
      to_replace:
        1: "poor"
        2: "poor"
        3: "average"
        4: "good"
        5: "good"
    ```

    **Ouput**

    article | rating | rating_category
    :------:|:------:|:--------------:
    book    | 1      | poor
    puzzle  | 3      | average
    food    | 5      | good
    """
    new_column = new_column or column
    df.loc[:, new_column] = df[column].replace(**kwargs)
    return df

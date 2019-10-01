import pandas as pd


def convert_str_to_datetime(df, *, column: str, format: str):
    """
    Convert string column into datetime column

    ---

    ### Parameters

    *mandatory :*
    - `column` (*str*): name of the column to format
    - `format` (*str*): current format of the values (see [available formats](
    https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior))
    """
    df[column] = pd.to_datetime(df[column], format=format)
    return df


def convert_datetime_to_str(df, *, column: str, format: str, new_column: str = None):
    """
    Convert datetime column into string column

    ---

    ### Parameters

    *mandatory :*
    - column (*str*): name of the column to format
    - format (*str*): format of the result values (see [available formats](
    https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior))

    *optional :*
    - new_column (*str*): name of the output column. By default `column` is overwritten.
    """
    new_column = new_column or column
    df[new_column] = df[column].dt.strftime(format)
    return df


def change_date_format(
    df,
    *,
    column: str,
    output_format: str,
    input_format: str = None,
    new_column: str = None,
    new_time_zone=None,
):
    """
    Convert the format of a date

    ---

    ### Parameters

    *mandatory :*
    - `column` (*str*): name of the column to change the format
    - `output_format` (*str*): format of the output values (see [available formats](
    https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior))

    *optional :*
    - `input_format` (*str*): format of the input values (by default let the parser detect it)
    - `new_column` (*str*): name of the output column  (by default overwrite `column`)
    - `new_time_zone` (*str*): name of new time zone (by default no time zone conversion is done)

    ---

    ### Example

    **Input**

    label   | date
    :------:|:----:
    France  | 2017-03-22
    Europe  | 2016-03-22

    ```cson
    change_date_format:
      column: 'date'
      input_format: '%Y-%m-%d'
      output_format: '%Y-%m'
    ```

    Output :

    label   | date
    :------:|:----:
    France  | 2017-03
    Europe  | 2016-03
    """
    new_column = new_column or column
    df[new_column] = (
        pd.to_datetime(df[column], format=input_format, utc=True)
        .dt.tz_convert(new_time_zone)
        .dt.strftime(output_format)
    )
    return df


def cast(df, column: str, type: str, new_column=None):
    """
    Convert column's type into type

    ---

    ### Parameters

    *mandatory :*
    - `column` (*str*): name of the column to convert
    - `type` (*str*): output type. It can be :
        - `"int"` : integer type
        - `"float"` : general number type
        - `"str"` : text type

    *optional :*
    - `new_column` (*str*): name of the output column.
       By default the `column` arguments is modified.

    ---

    ### Example

    **Input**

    | Column 1 |  Column 2   |  Column 3  |
    |:-------:|:--------:|:--------:|
    |  'one'  |  '2014'  |   30.0   |
    |  'two'  |  2015.0  |    '1'   |
    |   3.1   |   2016   |    450   |

    ```cson
    postprocess: [
      cast:
        column: 'Column 1'
        type: 'str'
      cast:
        column: 'Column 2'
        type: 'int'
      cast:
        column: 'Column 3'
        type: 'float'
    ]
    ```

    **Output**

    | Column 1 |  Column 2  |  Column 3  |
    |:-------:|:------:|:--------:|
    |  'one'  |  2014  |   30.0   |
    |  'two'  |  2015  |    1.0   |
    |  '3.1'  |  2016  |  450.0   |
    """
    new_column = new_column or column
    df[new_column] = df[column].astype(type)
    return df

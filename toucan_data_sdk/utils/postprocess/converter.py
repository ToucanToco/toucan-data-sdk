import pandas as pd


def convert_str_to_datetime(df, *, column=None, format=None):
    """
    Convert string column into datetime column

    - column: name of the column to format
    - format: current format of the values
    List of available format:
    https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
    """
    df[column] = pd.to_datetime(df[column], format=format)
    return df


def convert_datetime_to_str(df, *, column=None, format=None, new_column=None):
    """
    Convert datetime column into string column

    - column: name of the column to format
    - new_column: name of the output
    - format: format of the result values
    List of available format:
    https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
    """
    new_column = new_column or column
    df[new_column] = df[column].dt.strftime(format)
    return df


def change_date_format(
        df, *, column: str, output_format: str,
        input_format: str = None, new_column: str = None, new_time_zone=None):
    """
    Convert a date column from a format (input_format) to an other (output_format)
    ---
    - `column` (str): name of the column to change the format
    - `output_format` (str): format of the output values
    - `input_format` (optional: str): format of the input values - if 'None' let the parser detect it # noqa: E501
    - `new_column` (optional: str): name of the output column - if 'None' overwrite column
    - `new_time_zone` (optional: str): name of new time zone - if 'None', no time zone conversion is done  # noqa: E501
    [See the list of available format](
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior)
    """
    new_column = new_column or column
    df[new_column] = (pd.to_datetime(df[column], format=input_format, utc=True)
                      .dt.tz_convert(new_time_zone)
                      .dt.strftime(output_format))
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

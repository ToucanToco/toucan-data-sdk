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


def change_date_format(df, *, column: str, output_format: str, input_format=None, new_column=None,
                       new_time_zone=None):
    """
    Convert a date column from a format (input_format) to an other (output_format)

    - column: name of the column to change the format
    - output_format: format of the output values
    - input_format (optional): format of the input values - if 'None' let the parser detect it
    - new_column (optional): name of the output column - if 'None' overwrite column
    - new_time_zone (optional): name of new time zone - if 'None', no time zone conversion is done
    List of available format:
    https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
    """
    new_column = new_column or column
    df[new_column] = (pd.to_datetime(df[column], format=input_format, utc=True)
                      .dt.tz_convert(new_time_zone)
                      .dt.strftime(output_format))
    return df


def cast(df, column: str, type: str, new_column=None):
    """
    Convert column's type into type

    - column: name of the column to format
    - type: desired type of the column
    - new_column (optional): name of the output column - if 'None' overwrite column
    Available type : 'str' (from string), 'int' (for integer), 'float' (for real number)
    """
    new_column = new_column or column
    df[new_column] = df[column].astype(type)
    return df

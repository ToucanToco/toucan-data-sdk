def add(df, new_column, column_1, column_2):
    """
    Basic mathematical operation to add column_1 and column_2 values.
    Will create a new column named `new_column`
    """
    df[new_column] = df[column_1] + df[column_2]
    return df


def subtract(df, new_column, column_1, column_2):
    """
    Basic mathematical operation to substract column_2 to column_1 values.
    Will create a new column named `new_column`
    """
    df[new_column] = df[column_1] - df[column_2]
    return df


def multiply(df, new_column, column_1, column_2):
    """
    Basic mathematical operation to multiply column_1 and column_2 values.
    Will create a new column named `new_column`
    """
    df[new_column] = df[column_1] * df[column_2]
    return df


def divide(df, new_column, column_1, column_2):
    """
    Basic mathematical operation to divide column_2 to column_1 values.
    Will create a new column named `new_column`
    """
    df[new_column] = df[column_1] / df[column_2]
    return df

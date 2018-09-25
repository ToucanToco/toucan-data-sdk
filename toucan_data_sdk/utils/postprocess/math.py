import operator as _operator

import re

ALLOWED_FORMULA_CHARACTERS = '()+-/*%.'
FORMULA_REGEX = '(' + '|'.join([f'\{x}' for x in ALLOWED_FORMULA_CHARACTERS]) + ')'


def _basic_math_operation(df, new_column, column_1, column_2, op):
    """
    Basic mathematical operation to apply operator on `column_1` and `column_2`
    Both can be either a number or the name of a column of `df`
    Will create a new column named `new_column`
    """
    if not isinstance(column_1, (str, int, float)):
        raise TypeError(f'column_1 must be a string, an integer or a float')
    if not isinstance(column_2, (str, int, float)):
        raise TypeError(f'column_2 must be a string, an integer or a float')

    if isinstance(column_1, str):
        column_1 = df[column_1]
    if isinstance(column_2, str):
        column_2 = df[column_2]
    operator = getattr(_operator, op)
    df[new_column] = operator(column_1, column_2)
    return df


def add(df, new_column, column_1, column_2):
    """Add df[value] (value: 'str') or value (number) to column_1"""
    return _basic_math_operation(df, new_column, column_1, column_2, op='add')


def subtract(df, new_column, column_1, column_2):
    """Subtract df[value] (value: 'str') or value (number) to column_1"""
    return _basic_math_operation(df, new_column, column_1, column_2, op='sub')


def multiply(df, new_column, column_1, column_2):
    """Multiply df[value] (value: 'str') or value (number) and column_1"""
    return _basic_math_operation(df, new_column, column_1, column_2, op='mul')


def divide(df, new_column, column_1, column_2):
    """Divide df[value] (value: 'str') or value (number) to column_1"""
    return _basic_math_operation(df, new_column, column_1, column_2, op='truediv')


def is_words(s):
    return all(x.isalpha() or x.isspace() for x in s)


def is_float(x):
    try:
        float(x)
    except ValueError:
        return False
    else:
        return True


def formula(df, *, dst_column, formula):
    """Compute math formula for df and put the result in `column`"""
    splitted = [x.strip() for x in re.split(FORMULA_REGEX, formula) if x.strip()]
    expression_splitted = []
    for x in splitted:
        if not is_words(x):
            if x not in ALLOWED_FORMULA_CHARACTERS and not is_float(x):
                allowed = [f'"{x}"' for x in ALLOWED_FORMULA_CHARACTERS]
                raise FormulaError(f'"{x}" is not valid. Allowed entries are numbers, column '
                                   f'names and math symbols (among {", ".join(allowed)})')
            expression_splitted.append(x)
        else:
            if x not in df.columns:
                raise FormulaError(f'"{x}" is not a valid column name')
            expression_splitted.append(f'df["{x}"]')
    expression = ''.join(expression_splitted)
    df[dst_column] = eval(expression)
    return df


class FormulaError(Exception):
    """Raised when a formula is not valid"""

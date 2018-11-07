import operator as _operator

MATH_CHARACTERS = '()+-/*%.'


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


def is_float(x):
    try:
        float(x)
    except ValueError:
        return False
    else:
        return True


def _parse_formula(formula_str):
    splitted = []
    current_word = ''
    quote_to_match = None
    for x in formula_str:
        if x in ('"', "'") and not quote_to_match:
            quote_to_match = x
            continue
        if x == quote_to_match:
            splitted.append(current_word)
            current_word = ''
            quote_to_match = None
            continue
        if quote_to_match or x not in MATH_CHARACTERS:
            current_word += x
        else:
            splitted.append(current_word)
            current_word = ''
            splitted.append(x)
    splitted.append(current_word)
    if quote_to_match is not None:
        raise FormulaError('Missing closing quote in formula')
    return [x.strip() for x in splitted if x.strip()]


def formula(df, *, new_column, formula):
    """Compute math formula for df and put the result in `column`"""
    splitted = _parse_formula(formula)
    expression_splitted = []
    for x in splitted:
        if x in MATH_CHARACTERS or is_float(x):
            expression_splitted.append(x)
        elif x in df.columns:
            expression_splitted.append(f'df["{x}"]')
        else:
            raise FormulaError(f'"{x}" is not a valid column name')
    expression = ''.join(expression_splitted)
    df[new_column] = eval(expression)
    return df


class FormulaError(Exception):
    """Raised when a formula is not valid"""

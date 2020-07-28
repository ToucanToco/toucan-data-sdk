import logging
import operator as _operator
from typing import List

LOGGER = logging.getLogger(__name__)

MATH_CHARACTERS = '()+-/*%.'
DEPRECATED_COLUMN_QUOTE_CHARS = ('"', "'")
COLUMN_QUOTE_CHARS = ('`',)


def _basic_math_operation(df, new_column, column_1, column_2, op):
    """
    Basic mathematical operation to apply operator on `column_1` and `column_2`
    Both can be either a number or the name of a column of `df`
    Will create a new column named `new_column`
    """
    if not isinstance(column_1, (str, int, float)):
        raise TypeError('column_1 must be a string, an integer or a float')
    if not isinstance(column_2, (str, int, float)):
        raise TypeError('column_2 must be a string, an integer or a float')

    if isinstance(column_1, str):
        column_1 = df[column_1]
    if isinstance(column_2, str):
        column_2 = df[column_2]
    operator = getattr(_operator, op)
    df[new_column] = operator(column_1, column_2)
    return df


def add(df, new_column, column_1, column_2):
    """
    DEPRECATED -  use `formula` instead
    """
    return _basic_math_operation(df, new_column, column_1, column_2, op='add')


def subtract(df, new_column, column_1, column_2):
    """
    DEPRECATED -  use `formula` instead
    """
    return _basic_math_operation(df, new_column, column_1, column_2, op='sub')


def multiply(df, new_column, column_1, column_2):
    """
    DEPRECATED -  use `formula` instead
    """
    return _basic_math_operation(df, new_column, column_1, column_2, op='mul')


def divide(df, new_column, column_1, column_2):
    """
    DEPRECATED -  use `formula` instead
    """
    return _basic_math_operation(df, new_column, column_1, column_2, op='truediv')


def is_float(x):
    try:
        float(x)
    except ValueError:
        return False
    else:
        return True


class Token:
    """
    A formula is a string like this '"2018  " - 2017 + (a - b)'
    In order to parse it, we split it in different tokens and keep track if it was
    quoted or not.
    E.g. in the formula above, `2017` is a number whereas `"2018"` is a column name.
    even though both are strings.
    """

    def __init__(self, text: str, quoted: bool = False):
        self.text = text.strip()
        self.quoted = quoted

    def get_text(self) -> str:
        if not self.quoted and (self.text in MATH_CHARACTERS or is_float(self.text)):
            return self.text
        else:
            return f'`{self.text}`'

    def __len__(self):
        return len(self.text)

    def __repr__(self):
        return repr(self.text)

    def __eq__(self, other):
        return repr(self) == repr(other)


def _parse_formula(formula_str, quote_chars=COLUMN_QUOTE_CHARS) -> List[Token]:
    tokens = []
    current_word = ''
    quote_to_match = None
    for x in formula_str:
        if x in quote_chars and not quote_to_match:
            quote_to_match = x
            continue
        if x == quote_to_match:
            tokens.append(Token(current_word, True))
            current_word = ''
            quote_to_match = None
            continue
        if quote_to_match or x not in MATH_CHARACTERS:
            current_word += x
        else:
            tokens.append(Token(current_word))
            current_word = ''
            tokens.append(Token(x))
    tokens.append(Token(current_word))
    if quote_to_match is not None:
        raise FormulaError('Missing closing quote in formula')
    return [t for t in tokens if t]


def get_new_syntax_formula(formula: str) -> str:
    """
    Now that all columns must explicitly be quoted, we need a function
    to get the new syntax from the deprecated one
    """
    tokens = _parse_formula(formula, quote_chars=DEPRECATED_COLUMN_QUOTE_CHARS)
    return ''.join(t.get_text() for t in tokens)


def formula(df, *, new_column: str, formula: str):
    """
    Do mathematic operations on columns (add, subtract, multiply or divide)

    ---

    ### Parameters

    *mandatory:*
    - `new_column` (*str*): name of the output column
    - `formula` (*str*): Operation on column. Use name of column and special character:
        - `+` for addition
        - `-` for subtraction
        - `*` for multiplication
        - `/` for division

    **Note:**
    your column name must be quoted with backtick `

    ---

    ### Examples

    **Input**

    | variable | valueA | valueB | My rate |
    |:--------:|:--------:|:-----:|:------:|
    |   toto   |    20    |  100  |   10   |
    |   toto   |    30    |  200  |   10   |
    |   toto   |    10    |  300  |   10   |


    ```cson
    formula:
      new_column: 'valueD'
      formula: '(`valueB` + `valueA` ) / `My rate`'
    ```

    **Output**

    | variable | valueA   | valueB |  My rate |  valueD |
    |:--------:|:--------:|:------:|:-------:|:-------:|
    |   toto   |    20    |   100  |    10   |     12  |
    |   toto   |    30    |   200  |    10   |     23  |
    |   toto   |    10    |   300  |    10   |     31  |

    ---

    **Input**

    | variable | 2018 | 2019 |
    |:--------:|:--------:|:-----:|
    |   toto   |    20    |  100  |
    |   toto   |    30    |  200  |
    |   toto   |    10    |  300  |

    ```cson
    formula:
      new_column: 'Evolution'
      formula: "`2019` - `2018`"
    ```

    **Output**

    | variable | 2018 | 2019 | Evolution |
    |:--------:|:--------:|:-----:|:-----:|
    |   toto   |    20    |  100  | 80 |
    |   toto   |    30    |  200  | 170 |
    |   toto   |    10    |  300  | 290 |

    """
    if '`' not in formula:  # OLD SYNTAX
        old_formula = formula
        formula = get_new_syntax_formula(old_formula)
        LOGGER.warning(
            f'DEPRECATED: You should always use ` for your columns. '
            f'Old syntax: {old_formula!r}, new syntax: {formula!r}'
        )
    tokens = _parse_formula(formula)
    expression_splitted = []
    for t in tokens:
        # To use a column name with only digits, it has to be quoted!
        # Otherwise it is considered as a regular number
        if not t.quoted and (t.text in MATH_CHARACTERS or is_float(t.text)):
            expression_splitted.append(t.text)
        elif t.text in df.columns:
            expression_splitted.append(f'df["{t.text}"]')
        else:
            raise FormulaError(f'"{t.text}" is not a valid column name')
    expression = ''.join(expression_splitted)
    df[new_column] = eval(expression)
    return df


class FormulaError(Exception):
    """Raised when a formula is not valid"""


def round_values(df, *, column: str, decimals: int, new_column: str = None):
    """
    Round each value of a column

    ---

    ### Parameters

    *mandatory :*
    - `column` (*str*): name of the column to round
    - `decimals` (*int*): number of decimal to keeep

    *optional :*
    - `new_column` (*str*): name of the new column to create.
      By default, no new column will be created and `column` will be replaced

    ---

    ### Example

    ** Input**

    ENTITY|VALUE_1|VALUE_2
    :-----:|:-----:|:-----:
    A|-1.512|-1.504
    A|0.432|0.14

    ```cson
    round_values:
      column: 'VALUE_1'
      decimals:1
      new_column: 'Pika'
    ```

    **Output**

    ENTITY|VALUE_1|VALUE_2|Pika
    :-----:|:-----:|:-----:|:-----:
    A|-1.512|-1.504|-1.5
    A|0.432|0.14|0.4
    """
    new_column = new_column or column
    df[new_column] = df[column].round(decimals)
    return df


def absolute_values(df, *, column: str, new_column: str = None):
    """
    Get the absolute numeric value of each element of a column

    ---

    ### Parameters

    *mandatory :*
    - `column` (*str*): name of the column

    *optional :*
    - `new_column` (*str*): name of the column containing the result.
      By default, no new column will be created and `column` will be replaced.

    ---

    ### Example

    **Input**

    | ENTITY | VALUE_1 | VALUE_2 |
    |:------:|:-------:|:-------:|
    | A      | -1.512  | -1.504  |
    | A      | 0.432   | 0.14    |

    ```cson
    absolute_values:
      column: 'VALUE_1'
      new_column: 'Pika'
    ```

    **Output**

    | ENTITY | VALUE_1 | VALUE_2 | Pika  |
    |:------:|:-------:|:-------:|:-----:|
    | A      | -1.512  | -1.504  | 1.512 |
    | A      | 0.432   | 0.14    | 0.432 |
    """
    new_column = new_column or column
    df[new_column] = abs(df[column])
    return df

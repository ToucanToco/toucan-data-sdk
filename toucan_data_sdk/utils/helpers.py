from typing import List


def check_params_columns_duplicate(cols_name: List[str]) -> bool:
    params = [column for column in cols_name if column is not None]
    if len(set(params)) != len(params):
        duplicates = set([x for x in params if params.count(x) > 1])
        raise ParamsValueError(
            f'Duplicate declaration of column(s) {duplicates} in the parameters')
    else:
        return True


class ParamsValueError(Exception):
    """
    Exception raised when some parameters value are wrong
    """

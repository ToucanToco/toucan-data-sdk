import numpy as np

from toucan_data_sdk.utils.helpers import ParamsValueError


def randomize_values(serie, inf_bound, sup_bound):
    """
    Multiply a serie's values by a random value between [inf_bound, sup_bound)
    For example :

    Given this DataFrame:

       value
    0      1
    1      2
    2      3
    3      4
    4      5
    5      6

    df['res'] = randomize_values(df['value'], 0.85, 1.15) will give

       value       res
    0      1  1.047960
    1      2  2.293817
    2      3  3.246201
    3      4  3.574529
    4      5  4.832587
    5      6  5.547461

    Args:
        serie (pd.Serie):
        inf_bound (float):
        sup_bound (float):
    """
    if inf_bound >= sup_bound:
        raise ParamsValueError("The inferior bound should be inferior to the superior bound.")

    random_values = (sup_bound - inf_bound) * np.random.random_sample((len(serie),)) + inf_bound
    return serie * random_values

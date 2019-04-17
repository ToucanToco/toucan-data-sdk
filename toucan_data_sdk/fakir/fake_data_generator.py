from itertools import product
from typing import List

import numpy as np
import pandas as pd


def fake_data_generator(conf: List[dict]) -> pd.DataFrame:
    """
    `conf` is a list of dictionaries like
      {'type': 'label', 'values': ['Paris', 'Marseille', 'Lyons'], 'name': 'Cities'}
    and each dictionary will add a column.

    There are two different behaviours:
    - type: 'label' -> the new column will be taken into account for a cartesian product
                       with all other labels
    - type: 'number' -> the new column will contain simple numbers
    """

    # First create all the lines with the cartesian product of all the
    # possible values of 'label' columns
    label_confs = [x for x in conf if x['type'] == 'label']
    label_names = [x['name'] for x in label_confs]
    label_values = [x['values'] for x in label_confs]
    df = pd.DataFrame(list(product(*label_values)), columns=label_names)

    # Then add all the 'number' columns
    number_confs = [x for x in conf if x['type'] == 'number']
    for num_conf in number_confs:
        num_column = np.random.uniform(low=num_conf['min'], high=num_conf['max'], size=df.shape[0])
        df[num_conf['name']] = num_column.round(num_conf.get('digits', 4))

    return df

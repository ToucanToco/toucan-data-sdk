import pandas as pd
import numpy as np
from itertools import product


def fake_data_generator(conf):
    label_values = [x['values'] for x in conf if x['type'] == 'label']
    label_names = [x['name'] for x in conf if x['type'] == 'label']
    numbers = [x for x in conf if x['type'] == 'number']

    df = pd.DataFrame(list(product(*label_values)), columns=label_names)

    for num in numbers:
        df[num['name']] = np.random.uniform(low=num['min'], high=num['max'], size=len(df))
        df[num['name']] = df[num['name']].round(num['digits'])

    return df

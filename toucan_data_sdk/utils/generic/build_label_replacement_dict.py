import random

import pandas as pd
from faker import Faker


def change_vowels(label, name_generator, max_changed_vowels=2):
    """
    Outputs a label with the first max_changed_vowels changed
    When no vowels are present, a random name is chosen
    """
    copy = ''
    vowels = 'aeiouy'
    count = 0

    # if label is not a string with at least one vowel return a random name
    if not (isinstance(label, str) and any(x in vowels for x in label.lower())):
        return name_generator()

    for c in label:
        if count < max_changed_vowels and c.lower() in vowels:
            new_letter = random.choice([x for x in vowels if x != c.lower()])
            copy += new_letter.upper() if c.isupper() else new_letter
            count += 1
        else:
            copy += c

    return copy


def build_label_replacement_dict(serie, max_changed_vowels=2, override_values=None,
                                 name_generator=None):
    """
    Output a dict with anonymized names

    For example :

    NAMES
    Superman
    Wonderwoman
    Storm
    xxx

    `build_name_replacement_dict(names_serie)` with default arguments will output:
    {
        "Superman": "Sopurman",
        "Wonderwoman": "Wandurwoman",
        "Storm": "Starm",
        "xxx": "Lucy Cechtelar", # From the faker lib, when no vowels are present
    }

    `build_name_replacement_dict(
        names_serie,
        max_changed_vowels=3,
        override_values={"xxx": "yyy"}
    )`
    will output:
    {
        "Superman": "Sopurmin",
        "Wonderwoman": "Wandurweman",
        "Storm": "Starm",
        "xxx": "yyy",
    }

    Args:
        serie (pd.Series):
        max_changed_vowels (Integer):
        override_values (dict(str)):
        name_generator (function):
    """
    if name_generator is None:
        fake = Faker()
        name_generator = fake.name

    unique_values = serie.drop_duplicates()
    replacements_dict = {
        x: change_vowels(x, name_generator, max_changed_vowels=max_changed_vowels)
        for x in unique_values.values
    }
    # Prevent future errors in replacements
    skeys = set(replacements_dict.keys())
    svals = set(replacements_dict.values())
    intersection = skeys & svals
    if intersection:
        for key, value in replacements_dict.items():
            if value in intersection:
                replacements_dict[key] = value + ' ' + name_generator()

    # Overrides
    if override_values is not None:
        replacements_dict.update(override_values)
    return replacements_dict

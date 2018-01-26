import pytest
import pandas as pd

from toucan_data_sdk.utils.generic import (
    randomize_values,
    change_vowels,
    build_label_replacement_dict
)
from toucan_data_sdk.utils.helpers import ParamsValueError


@pytest.fixture()
def name_generator():
    return lambda: 'toto'


def test_change_vowels(name_generator):
    """
    It should change vowels when possible, and create a new name when impossible
    """

    def changed_letters(x, y):
        return [i for i in range(len(x)) if x[i] != y[i]]

    word_with_vowels = "TurlUtutu"
    res = change_vowels(word_with_vowels, name_generator)
    assert changed_letters(word_with_vowels, res) == [1, 4]

    res = change_vowels(word_with_vowels, name_generator, 3)
    assert changed_letters(word_with_vowels, res) == [1, 4, 6]

    word_with_no_vowel = "qwqwqw"
    res = change_vowels(word_with_no_vowel, name_generator)
    assert res == name_generator()


def test_change_vowels_not_a_string(name_generator):
    """
    It should not break when the input is not a string
    """
    res = change_vowels(0.123, name_generator=name_generator)
    assert res == name_generator()


def test_build_label_replacement_dict(name_generator):
    """It should build a replacement dict"""
    labels = pd.Series(['TurlUtutu', 'special', 'xkcd'])

    res = build_label_replacement_dict(
        labels,
        name_generator=name_generator,
        max_changed_vowels=3,
        override_values={'special': 'snowflake'}
    )
    assert res['TurlUtutu'] != 'TurlUtutu'
    assert res['TurlUtutu'][6] != 'u'
    assert res['xkcd'] == name_generator()
    assert res['special'] == 'snowflake'


def test_build_label_replacement_dict_with_keys_matching_values(name_generator):
    """It should build a replacement dict"""
    labels = pd.Series(['toto', 'xkcd'])

    res = build_label_replacement_dict(
        labels,
        name_generator=name_generator,
    )
    assert res['toto'] != 'toto'
    assert res['xkcd'] != 'toto'


def test_build_label_replacement_dict_with_no_name_generator():
    """It should build a replacement dict"""
    labels = pd.Series(['toto', 'xkcd'])
    res = build_label_replacement_dict(
        labels,
    )
    assert res['toto'] != 'toto'
    assert res['xkcd'] != 'xkcd'


def test_randomize_values():
    """It should output a serie with values in the required bounds"""
    values = pd.Series([0, 1, 2, 3, 4, 5])
    inf_bound = 0.85
    sup_bound = 1.15
    min_values = values * inf_bound
    max_values = values * sup_bound

    randomized = randomize_values(values, inf_bound, sup_bound)

    in_bounds = (randomized <= max_values) & (randomized >= min_values)

    assert in_bounds.all()


def test_randomize_values_bounds_error():
    """It should raise a ParamsValueError when the bounds are incorrect"""

    with pytest.raises(ParamsValueError) as e_info:
        randomize_values(pd.Series([0, 1]), 1.1, 0.2)

    assert str(e_info.value) == "The inferior bound should be inferior to the superior bound."

from toucan_data_sdk.fakir import fake_data_generator, predict_number_of_row_from_conf

conf_1 = [
    {"type": "label", "values": ["Paris", "Marseille", "Lyons"], "name": "Cities"},
    {"type": "label", "values": ["A", "B", "C"], "name": "Agence_type"},
    {"type": "number", "min": 0, "max": 10, "name": "CA"},
]

conf_2 = conf_1 + [
    {"type": "number", "min": 10, "max": 100, "digits": 2, "name": "Percentage"},
    {"type": "label", "values": ["Man", "Women"], "name": "Sexe"},
]


def test_fake_data_generator():
    fake_data = fake_data_generator(conf_1)
    assert set(fake_data.columns) == {"Cities", "Agence_type", "CA"}
    assert fake_data.shape == (3 * 3, 3)
    assert fake_data["CA"].between(0, 10).all()
    assert fake_data["CA"].round(4).equals(fake_data["CA"])
    assert fake_data[fake_data["Cities"] == "Paris"].shape[0] == 3
    assert fake_data[fake_data["Agence_type"] == "A"].shape[0] == 3

    fake_data = fake_data_generator(conf_2)
    assert set(fake_data.columns) == {"Cities", "Agence_type", "CA", "Sexe", "Percentage"}
    assert fake_data["Percentage"].round(2).equals(fake_data["Percentage"])
    assert fake_data.shape == (3 * 3 * 2, 5)


def test_fake_data_generator_with_edge_case_conf():
    """It should not throw any errors"""
    # label has no `name` key
    fake_data_generator(
        [{"type": "label", "values": ["A", "B"]}, {"type": "number", "min": 0, "max": 25}]
    )
    # label has no `values` key:
    fake_data_generator(
        [{"type": "label", "name": "toto"}, {"type": "number", "min": 0, "max": 25}]
    )
    # label has neither `name` or `values` key
    fake_data_generator([{"type": "label"}, {"type": "number", "min": 0, "max": 25}])

    # number has no `name` key:
    fake_data_generator(
        [{"type": "label", "values": ["A", "B"], "name": "toto"}, {"type": "number", "min": 0}]
    )
    # number has no `max` key:
    fake_data_generator(
        [{"type": "label", "values": ["A", "B"], "name": "toto"}, {"type": "number", "min": 0}]
    )
    # number has no `min` key:
    fake_data_generator(
        [{"type": "label", "values": ["A", "B"], "name": "toto"}, {"type": "number", "max": -12}]
    )
    # number has neither `max` or `min` key:
    fake_data_generator(
        [{"type": "label", "values": ["A", "B"], "name": "toto"}, {"type": "number"}]
    )


def test_predict_number_of_row_from_conf():
    conf = [{"values": ["a", "b", "c"], "type": "label"}, {"min": 0, "max": 10, "type": "number"}]
    assert predict_number_of_row_from_conf(conf) == 3

    conf = [
        {"values": ["a", "b", "c"], "type": "label"},
        {"values": ["x", "y"], "type": "label"},
        {"min": 0, "max": 10, "type": "number"},
    ]
    assert predict_number_of_row_from_conf(conf) == 3 * 2

    conf = [
        {"values": ["a", "b", "c"], "type": "label"},
        {"values": ["x", "y"], "type": "label"},
        {"values": ["A", "B", "C", "D"], "type": "label"},
        {"min": 0, "max": 10, "type": "number"},
    ]
    assert predict_number_of_row_from_conf(conf) == 3 * 2 * 4


def test_predict_number_of_row_from_conf_edge_case():
    """It should not throw any errors"""
    conf = [{"min": 0, "max": 10, "type": "number", "name": "number"}]
    assert predict_number_of_row_from_conf(conf) == 0

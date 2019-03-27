from toucan_data_sdk.fakir import fake_data_generator


conf_1 = [
  {"type": "label", "values": ['Paris', 'Marseille', 'Lyons'], "name": "Cities"},
  {"type": "label", "values": ['A', 'B', 'C'], "name": "Agence_type"},
  {"type":"value", "min": 0, "max": 10, "digits": 2, "name": "CA"}
]

conf_2 = conf_1 + [
  {"type":"value", "min": 10, "max": 100, "digits": 4, "name": "Percentage"}
  {"type": "label", "values": ["Man", "Women"], "name": "Sexe"}
]


def test_fakir():
  fake_data = fake_data_generator(conf_1)

  assert set(fake_data.columns) == {"Cities", "Agence_type", "CA"}
  assert len(fake_data) == 3*3
  assert (fake_data['CA'] > 0).all() & (fake_data['CA'] < 10).all()
  assert (fake_data.round(decimals=2)['CA'] == fake_data['CA']).all()
  assert (fake_data['Cities'] == 'Paris').sum() == 2
  assert (fake_data['Agence_type'] == 'A').sum() == 2


  fake_data = fake_data_generator(conf_2)
  assert set(fake_data.columns) == {"Cities", "Agence_type", "CA", 'Sexe', 'Percentage'}
  assert len(fake_data) == 3*3*2

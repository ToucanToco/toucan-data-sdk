# Spreadsheets doc:
# https://drive.google.com/drive/folders/0B56th7Lb-9vScy0tMlpIeGNxQ0E

from .add_missing_row import add_missing_row
from .aggregate_for_requesters import aggregate_for_requesters
from .clean import clean_dataframe
from .compute_cumsum import compute_cumsum
from .compute_evolution import (
    compute_evolution,
    compute_evolution_by_criteria,
    compute_evolution_by_frequency
)
from .compute_ffill_by_group import compute_ffill_by_group
from .postprocess import (
    replace, rename,
    melt, top, pivot, pivot_by_group,
    argmax, fillna, query_df, query,
    add, subtract, multiply, divide, cumsum,
    percentage, waterfall
)
from .roll_up import roll_up
from .two_values_melt import two_values_melt
from .build_label_replacement_dict import (
    build_label_replacement_dict,
    change_vowels
)
from .randomize_values import randomize_values

import os
import sys

import pandas as pd
import pytest

cur_dir = os.getcwd()
src_path = cur_dir[
    : cur_dir.index("customer_complaint_analyzer") + len("customer_complaint_analyzer")
]
if src_path not in sys.path:
    sys.path.append(src_path)

from src.data.load_preprocess_data import load_and_preprocess_raw_complaints_data

raw_data_path = os.path.join("data", "raw", "complaints.csv")


def test_return_type():

    preprocessed_df = load_and_preprocess_raw_complaints_data(
        raw_data_path, num_rows=100
    )

    assert type(preprocessed_df) == pd.DataFrame


@pytest.mark.parametrize("nrows", [(1), (100), (100_000)])
def test_row_selection_options(nrows):

    preprocessed_df = load_and_preprocess_raw_complaints_data(
        raw_data_path, num_rows=nrows
    )

    assert len(preprocessed_df) == nrows


@pytest.mark.parametrize(
    "file_path", [(os.path.join("this", "path", "doesn't", "exist"))]
)
def test_incorrect_file_path(file_path):

    with pytest.raises(FileNotFoundError):
        preprocessed_df = load_and_preprocess_raw_complaints_data(file_path)

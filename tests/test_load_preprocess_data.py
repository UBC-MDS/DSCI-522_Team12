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

from src.data.load_preprocess_data import (
    load_and_preprocess_raw_complaints_data,
    load_processed_complaints_data,
)

raw_data_path = os.path.join("data", "raw", "complaints.csv")
processed_data_path = os.path.join("data", "processed", "preprocessed-complaints.csv")

"""DATA LOADING TESTS"""

# Test a basic call returns a pandas data frame
def test_raw_load_returns_dataframe():

    raw_df = load_and_preprocess_raw_complaints_data(raw_data_path, num_rows=100)

    assert type(raw_df) == pd.DataFrame


def test_processed_load_returns_dataframe():

    processed_df = load_processed_complaints_data(processed_data_path, num_rows=100)

    assert type(processed_df) == pd.DataFrame


# Test that the number of rows returned is equal to the number of rows requested
@pytest.mark.parametrize("nrows", [(1), (100), (100_000)])
def test_raw_row_selection_options(nrows):

    raw_df = load_and_preprocess_raw_complaints_data(raw_data_path, num_rows=nrows)

    assert len(raw_df) == nrows


@pytest.mark.parametrize("nrows", [(1), (100), (100_000)])
def test_processed_row_selection_options(nrows):

    processed_df = load_processed_complaints_data(processed_data_path, num_rows=nrows)

    assert len(processed_df) == nrows


# test that skipping first rows of dataframes returns the same data at the first
# row of the dataframe
@pytest.mark.parametrize("skip_rows", [(1), (100), (999)])
def test_raw_skip_row_selection_options(skip_rows):

    no_skip_df = load_and_preprocess_raw_complaints_data(raw_data_path, num_rows=1000)
    skip_rows_df = load_and_preprocess_raw_complaints_data(
        raw_data_path, num_rows=1000, skip_rows=skip_rows
    )

    assert no_skip_df.complaint_id.iloc[skip_rows] == skip_rows_df.complaint_id.iloc[0]


@pytest.mark.parametrize("skip_rows", [(1), (100), (999)])
def test_processed_skip_row_selection_options(skip_rows):

    no_skip_df = load_processed_complaints_data(processed_data_path, num_rows=1000)
    skip_rows_df = load_processed_complaints_data(
        processed_data_path, num_rows=1000, skip_rows=skip_rows
    )

    assert no_skip_df.complaint_id.iloc[skip_rows] == skip_rows_df.complaint_id.iloc[0]


"""FILE PATH TESTS"""

# Test that a non-existent file path raises a FileNotFoundError
@pytest.mark.parametrize(
    "file_path", [(os.path.join("this", "path", "doesn't", "exist"))]
)
def test_raw_incorrect_file_path(file_path):

    with pytest.raises(FileNotFoundError):
        raw_df = load_and_preprocess_raw_complaints_data(file_path)


@pytest.mark.parametrize(
    "file_path", [(os.path.join("this", "path", "doesn't", "exist"))]
)
def test_processed_incorrect_file_path(file_path):

    with pytest.raises(FileNotFoundError):
        preprocessed_df = load_processed_complaints_data(file_path)


# Test that a non-string file path raises a ValueError
@pytest.mark.parametrize("file_path", [(1), (1.0), (True), (None)])
def test_raw_incorrect_file_path_type(file_path):

    with pytest.raises(ValueError):
        raw_df = load_and_preprocess_raw_complaints_data(file_path)


@pytest.mark.parametrize("file_path", [(1), (1.0), (True), (None)])
def test_processed_incorrect_file_path_type(file_path):

    with pytest.raises(ValueError):
        preprocessed_df = load_processed_complaints_data(file_path)

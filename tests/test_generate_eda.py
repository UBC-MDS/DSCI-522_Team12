import os
import sys

import pandas as pd
import pytest
import altair as alt

cur_dir = os.getcwd()
src_path = cur_dir[
    : cur_dir.index("customer_complaint_analyzer") + len("customer_complaint_analyzer")
]

if src_path not in sys.path:
    sys.path.append(src_path)

# from src.utils.utils import save_chart
from src.data.load_preprocess_data import load_processed_complaints_data
from src.data.generate_eda import gen_unique_null_table
from src.data.generate_eda import plot_missing_values

# Loading the data for testing
raw_data_path = os.path.join("data", "raw", "complaints.csv")
train = os.path.join("data", "processed", "preprocessed-complaints.csv")
complaints_df = load_processed_complaints_data(train)


# Sample test
def test_sample():
    """
    Sample tests to assert if the tests pass
    """

    assert "a" == "a"

# Testing if the function returns a datatype
def test_return_unique_table():
    """
    Tests if the function returns a dataframe type
    """

    assert type(gen_unique_null_table(complaints_df)) == type(pd.DataFrame())

def test_return_plot():
    """
    Checks if the function returns the correct altair type chart
    """
    actual = type(alt.Chart())
    returned = type(plot_missing_values(complaints_df, 200))
    assert actual == returned

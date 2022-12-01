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

raw_data_path = os.path.join("data", "raw", "complaints.csv")

from src.data.generate_eda import save_table


def test_input_type():

    assert "a" == "a"

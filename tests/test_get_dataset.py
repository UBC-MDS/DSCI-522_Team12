import os
import sys

import pytest

cur_dir = os.getcwd()
src_path = cur_dir[
    : cur_dir.index("customer_complaint_analyzer") + len("customer_complaint_analyzer")
]
print(src_path)
if src_path not in sys.path:
    sys.path.append(src_path)

from src.data.get_dataset import main

raw_data_path = os.path.join("data", "raw", "complaints.csv")
url = 'https://files.consumerfinance.gov/ccdb/complaints.csv.zip'

# test that normal urls works and invalid url does not work
def test_response():

    response = main(
        url
    )
    
    failed_response = main(
        'This is not a url'
    )

    assert (response) == 0 and failed_response == -1

# test data is saved in the correct folder
def test_file_downloaded():

    response = main(
        url
    )
    
    assert response == 0 and os.path.exists(raw_data_path)


#!/usr/bin/env python
"""
Tools to load and preprocess raw and processed complaints data.

Example use:
raw_df = load_raw_complaints_data(
    os.path.join(os.pardir, "data", "raw", "complaints.csv")
)
# OR
raw_df = load_raw_complaints_data(
    os.path.join(os.pardir, "data", "raw", "complaints.csv"),
    num_rows = 200000, 
    skip_rows=100000
)
"""

from typing import Union

import pandas as pd


def load_raw_complaints_data(
    file_path: str, num_rows: Union[str, int] = "all", skip_rows: int = 0
) -> pd.DataFrame:
    """Reads in complaints data and cleans up names and data types.

    Parameters
    ----------
    file_path : string
        Relative location of the "complaints.csv" file
    num_rows : int, optional
        How many rows of the csv to read in to help speed up analysis. If all entire
        dataset is read in, by default "all"
    skip_rows : int, optional
        How many rows to skip from the start of the file, by default 0

    Returns
    -------
    pd.DataFrame
        The read in and cleaned data frame

    Raises
    ------
    ValueError
        Incorrect data types passed in for parameters.
    """

    # tell pandas we know there are mixed int/string values in these columns
    # these are coerced after reading in
    col_dtype_corrections = {"ZIP code": object, "Consumer disputed?": object}

    if num_rows == "all":
        raw_complaint_df = pd.read_csv(file_path, dtype=col_dtype_corrections)
    elif (type(num_rows) == int) & (type(skip_rows) == int):
        raw_complaint_df = pd.read_csv(
            file_path, dtype=col_dtype_corrections, nrows=num_rows, skiprows=skip_rows
        )
    else:
        raise ValueError(
            f"Expected num_rows as 'all' or integer and skip_rows as "
            f"integrer, got {type(num_rows)} and {type(skip_rows)}"
        )

    raw_complaint_df.columns = (
        raw_complaint_df.columns.str.lower()
        .str.replace(" ", "_")
        .str.replace("?", "", regex=False)
        .str.replace("-", "_")
    )

    # basic first infer of object_types
    raw_complaint_df = raw_complaint_df.infer_objects()

    # any columns with date in the name converted to datetime
    for col in [col for col in raw_complaint_df.columns if "date" in col]:
        raw_complaint_df[col] = pd.to_datetime(raw_complaint_df[col])

    # zip code column has non-permissable values, convert to numeric and NAN for bad vlaues
    raw_complaint_df.zip_code = pd.to_numeric(
        raw_complaint_df.zip_code,
        errors="coerce",
        downcast="integer",  # get into smallest data format
    )

    return raw_complaint_df

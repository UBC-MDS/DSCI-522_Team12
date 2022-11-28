"""
Generates EDA, tables and plots the pre-processed training data from the Customer Complaints
(from https://files.consumerfinance.gov/ccdb/complaints.csv.zip) and saves the plots as pdf and png files
Usage: src/generate_eda.py --train=<train> [--out_dir=<out_dir>]
Options:
--train=<train>          Path (including filename) to training data (saved as csv)
--out_dir=<out_dir>      Path to directory where the plots should be saved, optional
"""

# All the imports
from docopt import docopt
import sys
import os
import pandas as pd
import numpy as np
import altair as alt

cur_dir = os.getcwd()
SRC_PATH = cur_dir[
    : cur_dir.index("customer_complaint_analyzer") + len("customer_complaint_analyzer")
]
if SRC_PATH not in sys.path:
    sys.path.append(SRC_PATH)

from src.data.load_preprocess_data import load_and_preprocess_raw_complaints_data

# reading the docscript for the arguments
opt = docopt(__doc__)

# function that saves the table as a csv file
def save_table(table, table_name):
    """
    Saves the dataframe passed as a csv

    Args:
        table (pd.dataframe): dataframe to be saved as csv
    """
    table.to_csv(
        os.path.join(os.getcwd(), "reports", "assets", "tables", f"{table_name}.csv"),
        index=False,
    )


def main(train, out_dir):
    """
    Main function that saves some EDA plots and tables into the assets folder

    Args:
        train (string): path of the train data
        out_dir (string): path where the results need to be stored
    """

    if out_dir is None:
        out_dir = os.path.join("results", "assets")
    complaints_df = load_and_preprocess_raw_complaints_data(train)

    # Table 1: Saves the unique and valid values
    unique_df = pd.DataFrame()
    unique_df["columns"] = complaints_df.columns
    unique_df["valid_count"] = complaints_df.count(axis=0).reset_index()[0]
    unique_df["unique_count"] = complaints_df.nunique().reset_index()[0]

    print("Saving the Table in the \assets\tables folder")
    save_table(unique_df, table_name="unique_df")
    print("Table Saved")

    # Plot 1: Missing Values Plot
    print("Generating missing values plot")
    num_complaints = 2000
    alt.data_transformers.enable("data_server")
    na_val_df = (
        complaints_df.tail(num_complaints).isna().reset_index().melt(id_vars="index")
    )
    last_date = (
        complaints_df.date_received.tail(num_complaints).max().strftime("%m/%d/%Y")
    )
    first_date = (
        complaints_df.date_received.tail(num_complaints).min().strftime("%m/%d/%Y")
    )
    missing_vals = (
        alt.Chart(
            complaints_df.tail(num_complaints)
            .isna()
            .reset_index()
            .melt(id_vars="index"),
            title=f"Missing Values of {num_complaints} Complaints: {first_date} - {last_date}",
        )
        .mark_rect()
        .encode(
            alt.X("index:O", axis=None),
            alt.Y("variable", title=None),
            alt.Color("value", title="Missing Value", scale=alt.Scale(scheme="dark2")),
            alt.Stroke("value", scale=alt.Scale(scheme="dark2"))
            # We set the stroke which is the outline of each rectangle in the heatmap
        )
        .properties(width=min(500, complaints_df.tail(num_complaints).shape[0]))
    )
    print("Plot Generated")
    print("Saving the Missing Values plot")
    missing_vals.save(os.path.join(os.getcwd(), out_dir, "missing_values_plot.png"))
    print("Plot saved")

    # Plot 2: Complaints over time
    print("Generating complaints over time plot")
    num_complaints = (
        complaints_df.resample("M", on="date_received")
        .agg({"date_received": "size"})
        .rename(columns={"date_received": "num_complaints"})
        .reset_index()
    )
    complaints_over_time = (
        alt.Chart(num_complaints, title="Monthly Complaints are Spiking in 2022")
        .mark_line()
        .encode(
            x=alt.X("date_received:T", title="Date Complaints Received"),
            y=alt.Y("num_complaints:Q", title="No. of Monthly Complaints"),
        )
        .properties(width=700, height=400)
    )
    print("Plot generated - now saving it")
    complaints_over_time.save(
        os.path.join(os.getcwd(), out_dir, "complaints_over_time_line.png")
    )
    print("Plot saved")

    # Plot 3: Disputed Bar Chart
    print("Now generating consumer disputed bar chart")
    target = pd.DataFrame(complaints_df.value_counts("consumer_disputed")).reset_index()
    target.columns = ["consumer_disputed", "count"]
    disputed_cust = (
        alt.Chart(target, title="Majority of Complaints are Not Disputed")
        .mark_bar()
        .encode(
            y=alt.Y("consumer_disputed:O", title="Consumer Disputed"),
            x=alt.X("count:Q", title="No. of Complaints"),
            color=alt.Color("consumer_disputed:O", legend=None),
        )
        .properties(width=600, height=300)
    )
    print("Plot generated - now saving it in the assets folder")
    disputed_cust.save(os.path.join(os.getcwd(), out_dir, "disputed_bar.png"))
    print("Plot saved")


if __name__ == "__main__":
    main(opt["--train"], opt["--out_dir"])

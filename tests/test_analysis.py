import os
import sys

import pytest

cur_dir = os.getcwd()
src_path = cur_dir[
    : cur_dir.index("customer_complaint_analyzer") + len("customer_complaint_analyzer")
]
if src_path not in sys.path:
    sys.path.append(src_path)
from sklearn.pipeline import Pipeline
from src.analysis.analysis import *

data_filepath = 'data/processed/preprocessed-complaints.csv'
# load data set
complaints_df = load_processed_complaints_data(data_filepath)
complaints_df = complaints_df.query("not consumer_disputed.isnull()")
complaints_df["consumer_disputed"].replace(["Yes", "No"], [1, 0], inplace=True)

drop_features = [
    "date_received",
    "zip_code",
    "tags",
    "date_sent_to_company",
    "complaint_id",
]

complaints_df = complaints_df.drop(columns=drop_features).dropna()
train_df, test_df = train_test_split(complaints_df, test_size=0.2, random_state=123)
X_train, y_train = (
    train_df.drop(columns=["consumer_disputed"]),
    train_df["consumer_disputed"],
)
X_test, y_test = test_df.drop(columns= ['consumer_disputed']), test_df['consumer_disputed']

categorical_features = [
    "product",
    "sub_product",
    "issue",
    "sub_issue",
    "company_public_response",
    "company",
    "state",
    "consumer_consent_provided",
    "consumer_consent_provided",
    "submitted_via",
    "company_response_to_consumer",
    "timely_response",
]
drop_features = ["consumer_consent_provided", "submitted_via"]

text_feature = "consumer_complaint_narrative"

preprocessor = make_column_transformer(
    (
        OneHotEncoder(handle_unknown="ignore", drop="if_binary"),
        categorical_features,
    ),
    (CountVectorizer(stop_words="english", max_features=3000), text_feature),
    ("drop", drop_features),
)
scoring_metrics = ["accuracy", "recall", "precision", "f1"]

def test_dummy():

    df, pipe = train_dummy(
        X_train, y_train, preprocessor, scoring_metrics
    )
    # test dummy regressor returns correct type
    assert type(df) == pd.DataFrame  and type(pipe) == Pipeline
    assert float(df.iloc[5]) == 0.0
    
def test_lr():

    df, pipe = train_logreg(
        X_train, y_train, preprocessor, scoring_metrics
    )
    # test lr regressor returns correct type
    assert type(df) == pd.DataFrame  and type(pipe) == Pipeline
    
    assert float(df.iloc[5]) >= 0.3
    
def test_nb():

    df, pipe = train_nb(
        X_train, y_train, preprocessor, scoring_metrics
    )
    # test naive bernoulli regressor returns correct type
    assert type(df) == pd.DataFrame  and type(pipe) == Pipeline
    
    # test naive bernoulli regressor returns correct values for f1
    assert float(df.iloc[5]) >= 0.2
    
def test_svc():

    df, pipe = train_svc(
        X_train, y_train, preprocessor, scoring_metrics
    )
    # test svc regressor returns correct type
    assert type(df) == pd.DataFrame  and type(pipe) == Pipeline
    # test svc regressor returns correct values for f1
    assert float(df.iloc[5]) >= 0.3





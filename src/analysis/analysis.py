# author: Luke Yang
# date: 2022-11-25

"""
Perform the analysis and generate table/plot
Usage: src/get_dataset.py --data_filepath=<data_file> --out_filepath=<out_file>
Options:
--data_filepath=<data_file>        The path of the data that the analysis is based on
--out_filepath=<out_file>          The folder path of the analysis output
"""

import os
import sys
import altair as alt
import pandas as pd
import warnings
from docopt import docopt
from sklearn.model_selection import train_test_split
from sklearn.compose import make_column_transformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import cross_validate
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score

cur_dir = os.getcwd()
SRC_PATH = cur_dir[
    : cur_dir.index("customer_complaint_analyzer") + len("customer_complaint_analyzer")
]
if SRC_PATH not in sys.path:
    sys.path.append(SRC_PATH)
from src.utils.utils import *
from src.data.load_preprocess_data import load_processed_complaints_data

warnings.filterwarnings("ignore")


def main(data_filepath, out_filepath):
    """
    perform analysis using different models and generate the results
    """
    print(
        "Starting analysis. Note it is OK to see warnings about columns being set to zeros."
    )
    print("Loading dataset...")
    complaints_df = load_processed_complaints_data(data_filepath)

    target = pd.DataFrame(complaints_df.value_counts("consumer_disputed")).reset_index()
    target.columns = ["consumer_disputed", "count"]
    chart = alt.Chart(target).mark_bar().encode(
        x=alt.X("consumer_disputed:O", title="Consumer Disputed"),
        y=alt.Y("count:Q", title="Count"),
        color="consumer_disputed:O",
    )
    save_chart(chart,os.path.join(out_filepath, "class_imbalance.png"))
    unique_df = pd.DataFrame()
    unique_df["columns"] = complaints_df.columns
    unique_df["valid_count"] = complaints_df.count(axis=0).reset_index()[0]
    unique_df["unique_count"] = complaints_df.nunique().reset_index()[0]
    unique_df.to_csv(os.path.join(out_filepath, "unique_counts.csv"))

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
    print("Splitting dataset...")
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
    cross_val_results = {}
    
    print('Analyzing baseline model...')
    cross_val_results['dummy'], pipe_dc = \
        train_dummy(X_train, y_train, preprocessor, scoring_metrics)
    
    print('Analyzing logistic regression model...')
    cross_val_results['logreg'], pipe_lr = \
        train_logreg(X_train, y_train, preprocessor, scoring_metrics)
    
    print('Analyzing naive bayes model...')
    cross_val_results['bayes'], pipe_nb = \
        train_nb(X_train, y_train, preprocessor, scoring_metrics)
    
    print('Analyzing svc model...')
    cross_val_results['svc'], pipe_svc = \
        train_svc(X_train, y_train, preprocessor, scoring_metrics)
    
    print('Analyzing random forest model...')
    cross_val_results['random forest'], pipe_rf = \
        train_random_forest(X_train, y_train, preprocessor, scoring_metrics)
            
    res = pd.concat(cross_val_results, axis=1)
    res.columns = res.columns.droplevel(1)
    print("Saving tabular results...")
    res.to_csv(os.path.join(out_filepath, "results.csv"))

    res = res.reset_index()
    source = res[2:].melt(id_vars=["index"])
    source.columns = ["Metric", "Model", "Score"]
    source["Metric"] = source["Metric"].str.replace("test_", "")
    print("Generating the plot...")
    chart = alt.Chart(source).mark_bar().encode(
        x="Metric:O", y="Score:Q", color="Metric:N", column="Model:N"
    )
    save_chart(chart,os.path.join(out_filepath, "model_performance.png")) 
    
    # test set evaluation
    
    models = {'Dummy Classifier':pipe_dc, 
          'Logistic Regression':pipe_lr, 
          'Naive Bayes Classifier':pipe_nb,
          'Support Vector Classifier':pipe_svc,
          'Random Forest Classifier':pipe_rf}
    scores = []
    for model in models:
        models[model].fit(X_train,y_train)
        print('Analyzing with',model)
        scores.append([accuracy_score(models[model].predict(X_test), y_test),
              recall_score(models[model].predict(X_test), y_test),
              precision_score(models[model].predict(X_test), y_test),
              f1_score(models[model].predict(X_test), y_test)])
    pd.DataFrame(scores, index=models.keys(), columns =['Accuracy','Recall','Precision','F1']).T\
        .to_csv(os.path.join(out_filepath, "test_scores.csv"))
    
    
def train_random_forest(X_train, y_train, preprocessor, scoring_metrics):
    """train and validate using random forest classifier

    Parameters
    ----------
    X_train : pandas.DataFrame
        training features
    y_train : pandas.Series
        training target
    preprocessor: sklearn.compose.ColumnTransformer
        the data transformer for X_train
    scoring_metrics: List[str]
        a list of sklearn recognizable metrics for cross validation

    Returns
    -------
    pd.DataFrame
        The scores for given metrics
    sklearn.Pipeline
        estimator

    Example
    -------
    cross_val_results['test'] = \
        train_random_forest(X_train, y_train, preprocessor, scoring_metrics)
    """
    pipe_rf = make_pipeline(preprocessor, RandomForestClassifier(class_weight='balanced', random_state=123))
    return pd.DataFrame(cross_validate(
        pipe_rf, X_train, y_train, n_jobs=-1, scoring=scoring_metrics)).agg(['mean']).round(3).T, pipe_rf

def train_svc(X_train, y_train, preprocessor, scoring_metrics):
    """train and validate using SVC

    Parameters
    ----------
    X_train : pandas.DataFrame
        training features
    y_train : pandas.Series
        training target
    preprocessor: sklearn.compose.ColumnTransformer
        the data transformer for X_train
    scoring_metrics: List[str]
        a list of sklearn recognizable metrics for cross validation

    Returns
    -------
    pd.DataFrame
        The scores for given metrics
    sklearn.Pipeline
        estimator
    Example
    -------
    cross_val_results['test'] = \
        train_svc(X_train, y_train, preprocessor, scoring_metrics)
    """
    pipe_svc = make_pipeline(preprocessor, SVC(class_weight='balanced', random_state=123))
    return pd.DataFrame(cross_validate(
        pipe_svc, X_train, y_train, n_jobs=-1, scoring=scoring_metrics)).agg(['mean']).round(3).T, pipe_svc

def train_nb(X_train, y_train, preprocessor, scoring_metrics):
    """train and validate using naive bayes classifier

    Parameters
    ----------
    X_train : pandas.DataFrame
        training features
    y_train : pandas.Series
        training target
    preprocessor: sklearn.compose.ColumnTransformer
        the data transformer for X_train
    scoring_metrics: List[str]
        a list of sklearn recognizable metrics for cross validation

    Returns
    -------
    pd.DataFrame
        The scores for given metrics
    sklearn.Pipeline
        estimator

    Example
    -------
    cross_val_results['test'] = \
        train_nb(X_train, y_train, preprocessor, scoring_metrics)
    """
    pipe_nb = make_pipeline(preprocessor, BernoulliNB(alpha = 0.1))
    return pd.DataFrame(cross_validate(
        pipe_nb, X_train, y_train, n_jobs=-1, scoring=scoring_metrics)).agg(['mean']).round(3).T, pipe_nb

def train_logreg(X_train, y_train, preprocessor, scoring_metrics):
    """train and validate using logistic regression

    Parameters
    ----------
    X_train : pandas.DataFrame
        training features
    y_train : pandas.Series
        training target
    preprocessor: sklearn.compose.ColumnTransformer
        the data transformer for X_train
    scoring_metrics: List[str]
        a list of sklearn recognizable metrics for cross validation

    Returns
    -------
    pd.DataFrame
        The scores for given metrics
    sklearn.Pipeline
        estimator

    Example
    -------
    cross_val_results['test'] = \
        train_logreg(X_train, y_train, preprocessor, scoring_metrics)
    """
    pipe_lr = make_pipeline(preprocessor, LogisticRegression(max_iter=10000,random_state=123, class_weight='balanced'))
    return pd.DataFrame(cross_validate(
        pipe_lr, X_train, y_train, n_jobs=-1, scoring=scoring_metrics)).agg(['mean']).round(3).T, pipe_lr

def train_dummy(X_train, y_train, preprocessor, scoring_metrics):
    """train and validate using dummy classifier

    Parameters
    ----------
    X_train : pandas.DataFrame
        training features
    y_train : pandas.Series
        training target
    preprocessor: sklearn.compose.ColumnTransformer
        the data transformer for X_train
    scoring_metrics: List[str]
        a list of sklearn recognizable metrics for cross validation

    Returns
    -------
    pd.DataFrame
        The scores for given metrics
    sklearn.Pipeline
        estimator
        
    Example
    -------
    cross_val_results['test'] = \
        train_dummy(X_train, y_train, preprocessor, scoring_metrics)
    """
    pipe_dc = make_pipeline(preprocessor, DummyClassifier())
    return pd.DataFrame(cross_validate(
        pipe_dc, X_train, y_train,scoring=scoring_metrics)).agg(['mean']).round(3).T, pipe_dc



if __name__ == "__main__":
    opt = docopt(__doc__)
    main(opt["--data_filepath"], opt["--out_filepath"])

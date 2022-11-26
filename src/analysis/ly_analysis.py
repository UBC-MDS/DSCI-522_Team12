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
warnings.filterwarnings("ignore")
opt = docopt(__doc__)


def main(data_filepath, out_filepath):
    """
    perform analysis using different models and generate the results
    """
    print('Starting analysis. Note it is OK to see warnings about columns being set to zeros.')
    print('Loading dataset...')
    complaints_df = pd.read_csv(data_filepath)
    
    target = pd.DataFrame(complaints_df.value_counts('consumer_disputed')).reset_index()
    target.columns = ['consumer_disputed','count']
    alt.Chart(target).mark_bar().encode(
        x=alt.X('consumer_disputed:O',title = 'Consumer Disputed'),
        y=alt.Y('count:Q',title = 'Count'),
        color='consumer_disputed:O',
    ).save(os.path.join(out_filepath,'class_imbalance.png'))
    unique_df = pd.DataFrame()
    unique_df['columns'] = complaints_df.columns
    unique_df['valid_count'] = complaints_df.count(axis=0).reset_index()[0]
    unique_df['unique_count'] = complaints_df.nunique().reset_index()[0]
    unique_df.to_csv(os.path.join(out_filepath,'unique_counts.csv'))
    complaints_df = complaints_df.iloc[: , 1:]
    complaints_df = complaints_df.query('not consumer_disputed.isnull()')
    complaints_df['consumer_disputed'].replace(['Yes','No'],[1,0], inplace = True)
    
    drop_features = ['date_received',
                    'zip_code',
                    'tags',
                    'date_sent_to_company',
                    'complaint_id']
    complaints_df = complaints_df.drop(columns = drop_features).dropna()
    print('Splitting dataset...')
    train_df, test_df = train_test_split(complaints_df,test_size=0.2, random_state=123)
    
    X_train, y_train = train_df.drop(columns= ['consumer_disputed']), train_df['consumer_disputed']
    # X_test, y_test = test_df.drop(columns= ['consumer_disputed']), train_df['consumer_disputed']
    
    categorical_features = ['product',
                            'sub_product',
                            'issue',
                            'sub_issue',
                            'company_public_response', 
                            'company',
                            'state',
                            'consumer_consent_provided',
                            'consumer_consent_provided',
                            'submitted_via',
                            'company_response_to_consumer',
                            'timely_response']
    drop_features = ['consumer_consent_provided',
                     'submitted_via']


    text_feature = 'consumer_complaint_narrative'

    preprocessor = make_column_transformer(
        (OneHotEncoder(handle_unknown = 'ignore',
                    drop='if_binary'), categorical_features),
        (CountVectorizer(stop_words='english', max_features = 3000), text_feature),
        ('drop', drop_features))
    scoring_metrics = ['accuracy','recall','precision','f1']
    cross_val_results = {}
    
    print('Analyzing baseline model...')
    pipe_dc = make_pipeline(preprocessor, DummyClassifier())
    pipe_dc.fit(X_train, y_train)
    cross_val_results['dummy'] = pd.DataFrame(cross_validate(
        pipe_dc, X_train, y_train,scoring=scoring_metrics)).agg(['mean']).round(3).T
    
    print('Analyzing logistic regression model...')
    pipe_lr = make_pipeline(preprocessor, LogisticRegression(max_iter=1000, class_weight='balanced'))
    cross_val_results['logreg'] = pd.DataFrame(cross_validate(
        pipe_lr, X_train, y_train, n_jobs=-1, scoring=scoring_metrics)).agg(['mean']).round(3).T
    cross_val_results['logreg']
    
    print('Analyzing naive bayes model...')
    pipe_nb = make_pipeline(preprocessor, BernoulliNB(alpha = 0.1))
    cross_val_results['bayes'] = pd.DataFrame(cross_validate(
        pipe_nb, X_train, y_train, n_jobs=-1, scoring=scoring_metrics)).agg(['mean']).round(3).T
    cross_val_results['bayes']
    
    print('Analyzing svc model...')
    pipe_svc = make_pipeline(preprocessor, SVC(class_weight='balanced'))
    cross_val_results['svc'] = pd.DataFrame(cross_validate(
        pipe_svc, X_train, y_train, n_jobs=-1, scoring=scoring_metrics)).agg(['mean']).round(3).T
    cross_val_results['svc']
    
    print('Analyzing random forest model...')
    pipe_rf = make_pipeline(preprocessor, RandomForestClassifier(class_weight='balanced'))
    cross_val_results['random forest'] = pd.DataFrame(cross_validate(
        pipe_rf, X_train, y_train, n_jobs=-1, scoring=scoring_metrics)).agg(['mean']).round(3).T
            
    res = pd.concat(cross_val_results, axis=1)
    res.columns = res.columns.droplevel(1)
    print('Saving tabular results...')
    res.to_csv(os.path.join(out_filepath,'results.csv'))
    
    res = res.reset_index()
    
    source = res[2:].melt(id_vars=['index'])
    source.columns = ['Metric','Model','Score']
    source['Metric'] = source['Metric'].str.replace('test_','')
    print('Generating the plot...')
    alt.Chart(source).mark_bar().encode(
        x='Metric:O',
        y='Score:Q',
        color='Metric:N',
        column='Model:N'
    ).save(os.path.join(out_filepath,'model_performance.png'))



if __name__ == "__main__":
    main(opt["--data_filepath"], opt["--out_filepath"])

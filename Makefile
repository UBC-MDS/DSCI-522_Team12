# customer complaint analysis
# author: Ty Andrews, Dhruvi Nishar, Luke Yang
# date: 2022-11-30

all: reports/final_report.qmd reports/final_report.pdf reports/final_report.html 

# download data
data/raw/complaints.csv: src/data/get_dataset.py
	python src/data/get_dataset.py --url=https://files.consumerfinance.gov/ccdb/complaints.csv.zip

# pre-process data (e.g., scale and split into train & test)
data/processed/preprocessed-complaints.csv : src/data/load_preprocess_data.py data/raw/complaints.csv
	python src/data/load_preprocess_data.py --raw_path="data/raw/complaints.csv" --output_path="data/processed/preprocessed-complaints.csv" 

# exploratory data analysis - visualize predictor distributions across classes
reports/assets/disputed_bar.png reports/assets/assets/complaints_over_time_line.png: src/data/generate_eda.py data/processed/preprocessed-complaints.csv
	python src/data/generate_eda.py --train=data/processed/preprocessed-complaints.csv --out_dir=reports/assets

# perform analysis 
eports/assets/results.csv eports/assets/model_performance.png: src/analysis/analysis.py data/processed/preprocessed-complaints.csv
	python src/analysis/analysis.py --data_filepath=data/processed/preprocessed-complaints.csv --out_filepath=reports/assets

# render report
reports/final_report.html: reports/final_report.qmd eports/assets/results.csv eports/assets/model_performance.png reports/assets/disputed_bar.png reports/assets/assets/complaints_over_time_line.png
	Rscript -e "rmarkdown::render('doc/breast_cancer_predict_report.Rmd', output_format = 'github_document')"

clean: 
	rm -rf data
	rm -rf results
	rm -rf doc/breast_cancer_predict_report.md doc/breast_cancer_predict_report.html
# Customer Complaint Predictor

Authors:  
- Ty Andrews  
- Dhruvi Nishar  
- Luke Yang  

A data science project for DSCI 522 (Data Science workflows); a
course in the Masters of Data Science program at the University of
British Columbia.

## Project proposal

We aim to investigate, analyze, and report using the [customer complaint dataset](#References)[1]. This dataset is published in in DATA.GOV and it is intended for public access and use. This dataset is a collection of customer complaints regarding their purchased financial products. It contains information on the summary and content of the complaint, the responses from the companies, and whether the customer disputed after companies response.

We aim to answer the following inferential and/or predictive questions: 
- **Can we predict whether a customer is going to dispute based on their complaint and the company's response?** This question may induce inferential sub-questions such as
- **What kind of response from the company is most likely to prevent the customer from disputing the service?**
- **When submitting a claim what is your probability of getting monetary compensation, responses in a timely manner etc. to give to consumers when submitting a complaint**
- **What kind of complaint cannot be easily resolved?** We will focus on the main question and target the subproblem if we have time.

We plan to analyze the data using a mix of tabular and natural language processing tools like the bag-of-words representation and apply proper numerical or categorical transformations to the customer's responses. We plan to construct the classification model using scalable models like `Naive Bayes` or `Ridge` regression. Given the size of the data, it might be challenging to apply complex models to train in the time we have. We may try complex models with a partition of the dataset to see the performance of other models.

Our exploratory analysis will mainly look into the company's responses rather than the customer's complaints. We will first split the data into training and test set. In the training set, we will visualize if the class is imbalanced to find the strategy of model building. A visualization determining whether a large number of unique values appear in a column will be created. 

## Accessing the data

You can run the following command in the root directory of this repo to retrieve the data
```
python src/data/get_dataset.py --url=https://files.consumerfinance.gov/ccdb/complaints.csv.zip
```

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

Please advise `CONTRIBUTING.md` for detailed information.
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

# References

<div id="refs" class="references hanging-indent">

<div id="ref-Dua2019">

[1] Publisher Consumer Financial Protection Bureau. (2020, November 10). Consumer complaint database. Catalog. Retrieved November 18, 2022, from https://catalog.data.gov/dataset/consumer-complaint-database 


</div>

</div>
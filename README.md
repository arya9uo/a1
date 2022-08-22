**student name:Jiajia Guo
**student id: 1135319

<h1 align="center">Factors Affecting the Use of Yellow Taxis in NYC</h1>

My research goal is to explore the factors affecting the use of yellow taxis in New York City such as Uber and Covid-19.
Besides, I implement linear regression and random forest to forecast
the tip amount for yellow taxis data based on information like fare amount, trip amount and so on.


Timeline: The timeline for the research is 11.2021-02.2022

* Install dependencies (Python 3.9)
```
pip install -r  requirements.txt
```

I use the instances between 11.2021-01.2022 as train and dev set, use instances in 02.2022 as test set.

To run the pipleline, please visit scripts directory

* download_dataset.py: This downloads Yellow Taxis and High Volume For-Hire Services Data and covid-19 between Nov 2021 and Feb 2022

* preprocess.py: This prepocesses covid-19 dataset, i.e. gets the daily new comfirmed cases and drops irrelevant columns and removes 
outliers in Yellow Taxis and High Volume For-Hire Services Data

* train.py: This samples instances from Yellow Taxis between 11.2021 and 01.2022 and splits them into train 
and dev set, also samples instances in 02.2022 for test set. Also implement linear regression and random forest models, train them, and evaluate them on dev and test sets with RMSE

* Please note that I make figures not only with python, but also with Tableau such as geospatial information.

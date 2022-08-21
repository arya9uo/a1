import pandas as pd
import glob
import numpy as np
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import mutual_info_regression
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor

train_dev_ratio = 0.2
dir = "../data/curated"
sample_train_ratio = 0.4
sample_test_ratio = 0.6


# Show the importance of features based on mutual_info_regression
def select_feature(X, y):
    k = X.shape[1]
    bestfeatures = SelectKBest(score_func=mutual_info_regression, k=k)
    fit = bestfeatures.fit(X, y)
    dfscores = pd.DataFrame(fit.scores_)
    dfcolumns = pd.DataFrame(X.columns)
    featureScores = pd.concat([dfcolumns, dfscores], axis=1)
    featureScores.columns = ['Feature', 'Score']  # name the dataframe columns
    print(featureScores.nlargest(k, 'Score'))  # print the score of all features


# split yellow taxis to train/dev/test
def split_dataset(best_features):
    X_train = []
    y_train = []

    X_test = []
    y_test = []

    for file in glob.glob(f"{dir}/yellow*.csv"):
        date = file.split("/")[-1].split(".csv")[0].split("_")[-1]
        df = pd.read_csv(file)
        all_features = best_features + ['tip_amount']
        new_df = df[all_features]
        if date != "2022-02":
            # random sample instances from Nov 2021 to Jan 2022
            new_df = new_df.sample(int(sample_train_ratio * len(new_df)))
            X_train += new_df[best_features].values.tolist()
            y_train += new_df.tip_amount.values.tolist()
        else:
            # random sample instances in Feb 2022 as test set
            new_df = new_df.sample(int(sample_test_ratio * len(new_df)))
            X_test += new_df[best_features].values.tolist()
            y_test += new_df.tip_amount.values.tolist()

    X_train = np.array(X_train)
    y_train = np.array(y_train)
    X_test = np.array(X_test)
    y_test = np.array(y_test)

    X_dev = X_train[:int(len(X_train) * train_dev_ratio)]
    y_dev = y_train[:int(len(y_train) * train_dev_ratio)]

    X_train = X_train[int(len(X_train) * train_dev_ratio):]
    y_train = y_train[int(len(y_train) * train_dev_ratio):]

    return X_train, y_train, X_dev, y_dev, X_test, y_test


if __name__ == "__main__":
    # probe the best features
    df = pd.read_csv(f"{dir}/yellow_tripdata_2021-11.csv")

    # score the importance of each feature (we don't consider total amount as it includes tip)
    cols = ["passenger_count", "trip_distance", 'RatecodeID',
            "PULocationID", "DOLocationID", "fare_amount",
            'payment_type', 'extra', 'mta_tax',
            'tolls_amount', 'improvement_surcharge',
            'congestion_surcharge', 'airport_fee', 'trip_time']
    new_df = df[cols]
    y = df.tip_amount
    select_feature(new_df, y)

    # 10 best features
    best_features = ["passenger_count", "trip_distance", 'RatecodeID',
                     "PULocationID", "DOLocationID", "fare_amount",
                     'extra', 'tolls_amount', 'airport_fee', 'trip_time']

    X_train, y_train, X_dev, y_dev, X_test, y_test = split_dataset(best_features)

    # implement liner regresion model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # evalute the performance of liner regresion model
    dev_preds = model.predict(X_dev)
    dev_rmse = mean_squared_error(y_dev, dev_preds, squared=False)

    test_preds = model.predict(X_test)
    test_rmse = mean_squared_error(y_test, test_preds, squared=False)

    print(f"RMSE on dev set is {dev_rmse}, RMSE on test set is {test_rmse}")

    # implement random forest model
    model = RandomForestRegressor(max_depth=4)
    model.fit(X_train, y_train)

    # evalute the performance of random forest model
    dev_preds = model.predict(X_dev)
    dev_rmse = mean_squared_error(y_dev, dev_preds, squared=False)

    test_preds = model.predict(X_test)
    test_rmse = mean_squared_error(y_test, test_preds, squared=False)

    print(f"RMSE on dev set is {dev_rmse}, RMSE on test set is {test_rmse}")

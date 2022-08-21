import pandas as pd
import glob
from collections import defaultdict
from datetime import datetime
import os



# calculate new confirmed covid-19 case from Nov 2021 to Feb 2022
def process_corona(path_2021="../data/raw/us-counties-2021.csv", path_2022="../data/raw/us-counties-2022.csv"):
    df_2021 = pd.read_csv(path_2021)
    df_2022 = pd.read_csv(path_2022)

    new_york_2021 = df_2021[
        (df_2021.county == "New York City") & (df_2021.date.str.split("-", expand=True)[1].astype(int) > 10)]
    new_york_2022 = df_2022[
        (df_2022.county == "New York City") & (df_2022.date.str.split("-", expand=True)[1].astype(int) < 3)]
    new_york = pd.concat((new_york_2021, new_york_2022))
    new_york = new_york.reset_index(drop=True)
    initial_new_case = int(df_2021[(df_2021.date == "2021-11-01") & (df_2021.county == "New York City")].cases) - \
                       int(df_2021[(df_2021.date == "2021-10-30") & (df_2021.county == "New York City")].cases)
    new_case = new_york.cases.diff().apply(lambda x: initial_new_case if x != x else x)
    new_york['new cases'] = new_case
    new_york.to_csv("new_york_corona.csv", index=False)

# preprocess yellow taxis and fhvhv
def preprocess(dir="data/curated"):
    files = glob.glob("data/raw/*.parquet")
    # convert parquet files to csv files
    for file in files:
        data = pd.read_parquet(file, engine="pyarrow")
        name = file.split(".")[0]
        data.to_csv(f"{name}.csv", index=False)

    if not os.path.exists(dir):
        os.mkdir(dir)

    for file in glob.glob("yellow*.csv"):
        df = pd.read_csv(file, parse_dates=['tpep_pickup_datetime', "tpep_dropoff_datetime"])
        # impute with most frequent values
        df = df.fillna(df.mode().iloc[0])

        # Filter RateCodeID to 1 and 2
        df = df[(df.RatecodeID == 1) | (df.RatecodeID == 2)]

        # Filter payment_type to 1 and 2
        df = df[(df.payment_type == 1) | (df.payment_type == 2)]

        # Remove store_and_fwd_flag
        df = df.drop("store_and_fwd_flag", axis=1)

        # trip_distance > 0
        df = df[df.trip_distance > 0]

        # tpep_pickup_datetime < tpep_dropoff_datetime
        df = df[df.tpep_pickup_datetime < df.tpep_dropoff_datetime]

        # the records should between 2021 and 2022
        df = df[(df.tpep_pickup_datetime.dt.year == 2021) | (df.tpep_pickup_datetime.dt.year == 2022)]

        # the month should be consistent with the file name
        df = df[df["tpep_pickup_datetime"].dt.month == int(file.split(".")[0].split("-")[-1])]

        # restrict to 263 taxi zones
        df = df[(df.PULocationID <= 263) & (df.DOLocationID <= 263)]

        # add trip time attributes (in seconds)
        df['trip_time'] = (df.tpep_dropoff_datetime - df.tpep_pickup_datetime).dt.total_seconds()

        # remove outliers
        df = df[(df.total_amount < 250) & (df.total_amount > 0) & (df.fare_amount < 180) & (df.fare_amount > 0) & (
                df.tip_amount < 180) & (df.tip_amount > 0) & (df.trip_time < 80000) & (df.trip_time > 0) & (
                        df.trip_distance < 400)]
        df.to_csv(file, index=False)

    for file in glob.glob("fhvhv*.csv"):
        df = pd.read_csv(file, parse_dates=['pickup_datetime', "dropoff_datetime"])

        # impute with most frequent values
        df = df.fillna(df.mode().iloc[0])

        # Filter to Uber
        df = df[df.hvfhs_license_num == "HV0003"]

        # Drop colomns
        df = df.drop(["dispatching_base_num", "originating_base_num", "request_datetime", "on_scene_datetime",
                      'shared_request_flag', 'shared_match_flag', 'access_a_ride_flag', 'wav_request_flag',
                      'wav_match_flag'], axis=1)

        # trip_miles > 0
        df = df[df.trip_miles > 0]

        # pickup_datetime < dropoff_datetime
        df = df[df.pickup_datetime < df.dropoff_datetime]

        # restrict to 263 taxi zones
        df = df[(df.PULocationID <= 263) & (df.DOLocationID <= 263)]

        # remove outliers
        df = df[(df.base_passenger_fare < 600) & (df.base_passenger_fare > 0) & (df.tips < 100) & (df.tips > 0) & (
                df.trip_time < 25000) & (df.trip_time > 0) & (df.trip_miles < 120) & (df.trip_miles > 0)]

        df.to_csv(f"{dir}/{file}", index=False)


if __name__ == "__main__":
    process_corona()
    if not os.path.exists("../data/curated"):
        os.makedirs("../data/curated")
    preprocess()

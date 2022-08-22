import wget
import os
import glob
import shutil


common_prefix = "https://d37ci6vzurychx.cloudfront.net/trip-data/"
cab_prefix = ["yellow", "fhvhv"]
timespan = ["2021-11", "2021-12", "2022-01", "2022-02"]
common_suffix = "parquet"

for cab in cab_prefix:
  url = common_prefix + cab + "_" "tripdata" + "_"
  for time in timespan:
    real_url = url + time + "." + common_suffix
    print(real_url)
    wget.download(real_url)
    

wget.download("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties-2022.csv")

wget.download("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties-2021.csv")


if not os.path.exists("data/raw"):
  os.makedirs("data/raw")

if not os.path.exists("data/curated"):
  os.makedirs("data/curated")
 

for file in glob.glob("*parquet"):
  shutil.move(file, "data/raw/")

for file in glob.glob("*csv"):
  shutil.move(file, "data/raw/")


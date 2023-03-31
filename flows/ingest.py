import pandas as pd
from sodapy import Socrata
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials
from pathlib import Path
import os


@task(retries=3,
      log_prints=True)
def fetch():
    columns = 'crime_id, offense_date, agency_crimetype_id, city, state, coord1, coord2, masked_address, location, category'
    client = Socrata("data.memphistn.gov", None)
    items = client.get_all("ybsi-jur4", select=columns) # for ALL rows
    # items = client.get("ybsi-jur4", select=columns, limit=300) # for testing first 300 rows
    df = pd.DataFrame.from_records(items)
    return df

@task(retries=3,
      log_prints=True)
def transform_data(raw_data):
    raw_data['city'] = raw_data['city'].rename({'MEMPHIS': 'Memphis', 'M': 'Memphis'})
    raw_data['offense_date_datetime'] = pd.to_datetime(raw_data['offense_date'])
    #raw_data['offense_date_day'] = raw_data['offense_date_datetime'].dt.date
    raw_data['coord1'] = raw_data['coord1'].astype(float)
    raw_data['coord2'] = raw_data['coord2'].astype(float)
    return raw_data

@task()
def write_local(df) -> Path:
    """Write DataFrame out locally as parquet file"""
    if not os.path.exists("data"):
        os.mkdir("data")
    path = Path("data/memphis_police_data.parquet")
    df.to_parquet(path, compression="gzip")
    return path

@task(log_prints=True)
def make_gcs_block():
    bucket_block = GcsBucket(
    gcp_credentials=GcpCredentials(service_account_file='../service_account.json'),
    bucket="memphis_police_data_lake_de-zoomcamp-final-project")
    bucket_block.save("final-project-bucket", overwrite=True)

@task(log_prints=True)
def write_to_gcs(path: Path):
    # upload to gcs
    gcs_block = GcsBucket.load('final-project-bucket')
    gcs_block.upload_from_path(from_path=path, to_path=path)
    os.remove(path)
    return

@flow()
def etl_web_to_gcs():
    """The main ETL function."""
    df = fetch()
    cleaned_df = transform_data(df)
    path = write_local(cleaned_df)
    make_gcs_block()
    write_to_gcs(path)

if __name__=='__main__':
    etl_web_to_gcs()
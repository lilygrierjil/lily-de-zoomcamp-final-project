# import other flows
from flows.ingest import etl_web_to_gcs
from flows.spark_job_flow import dataproc_flow
from flows.gcs_to_bq import etl_gcs_to_bq

from prefect import flow


@flow()
def main_flow():
    etl_web_to_gcs()
    etl_gcs_to_bq()
    dataproc_flow()

if __name__=='__main__':
    main_flow()
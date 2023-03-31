from prefect_gcp.bigquery import BigQueryWarehouse
from prefect_gcp import GcpCredentials
from prefect import flow, task

@task()
def get_gcp_credentials():
    return GcpCredentials(service_account_file='../service_account.json')


@task()
def create_external_table(gcp_credentials):
    #gcp_credentials_block = GcpCredentials.load("final-project-gcp-creds")

    with BigQueryWarehouse(gcp_credentials=gcp_credentials) as warehouse:
        create_operation = '''
        CREATE OR REPLACE EXTERNAL TABLE `memphis_police_data_all.external_memphis_police_data`
        OPTIONS (
        format = 'parquet',
        uris = ['gs://memphis_police_data_lake_de-zoomcamp-final-project/data/memphis_police_data.parquet']);
        '''

        warehouse.execute(create_operation)
        #return result

@task()
def create_partitioned_clustered_table(gcp_credentials):
    with BigQueryWarehouse(gcp_credentials=gcp_credentials) as warehouse:

        create_operation = '''
        CREATE OR REPLACE TABLE memphis_police_data_all.memphis_police_data_partitioned_clustered
        PARTITION BY date_trunc(offense_date_datetime, MONTH)
        CLUSTER BY category AS
        SELECT * FROM memphis_police_data_all.external_memphis_police_data;'''
        warehouse.execute(create_operation)
    # gcp_credentials_block = GcpCredentials.load("zoom-gcp-creds")

@flow(log_prints=True)
def etl_gcs_to_bq():
    gcp_credentials = get_gcp_credentials()
    create_external_table(gcp_credentials)
    create_partitioned_clustered_table(gcp_credentials)


if __name__=='__main__':
    etl_gcs_to_bq()
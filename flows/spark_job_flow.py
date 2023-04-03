from prefect import flow, task
from prefect.filesystems import LocalFileSystem
from google.cloud import dataproc, storage
import re
from prefect_gcp.cloud_storage import GcsBucket
import os

@task()
def upload_pyspark_job_to_gcs(from_path, to_path):
    gcs_block = GcsBucket.load('final-project-bucket')
    gcs_block.upload_from_path(from_path=from_path, to_path=to_path)


# code from https://github.com/PrefectHQ/prefect-gcp/issues/20
@task(log_prints=True)
def submit_dataproc_job(region, cluster_name, gcs_bucket, spark_filename, project_id):
    # Create the job client.
    job_client = dataproc.JobControllerClient(
        client_options={"api_endpoint": "{}-dataproc.googleapis.com:443".format(region)}
    )

    # Create the job config.
    job = {
        "placement": {"cluster_name": cluster_name},
        "pyspark_job": {
            "main_python_file_uri": "gs://{}/{}".format(gcs_bucket, spark_filename),
            "jar_file_uris": ["gs://spark-lib/bigquery/spark-bigquery-with-dependencies_2.12-0.23.2.jar"],
            "args": [os.environ['PROJECT_ID']]
        },
    }
    operation = job_client.submit_job_as_operation(
        request={"project_id": project_id, "region": region, "job": job}
    )

    response = operation.result()

    # Dataproc job output gets saved to the Google Cloud Storage bucket
    # allocated to the job. Use a regex to obtain the bucket and blob info.
    matches = re.match("gs://(.*?)/(.*)", response.driver_output_resource_uri)

    output = (
        storage.Client()
        .get_bucket(matches.group(1))
        .blob(f"{matches.group(2)}.000000000")
        .download_as_string()
    )

    print(f"Job finished successfully: {output}")


@flow()
def dataproc_flow():
    project_id = os.environ['PROJECT_ID']
    # upload_pyspark_job_to_gcs(from_path='/spark_code/spark_manipulations.py',
    #     to_path = 'spark_manipulations.py')
    submit_dataproc_job(region='us-central1', 
    cluster_name="mycluster", 
    gcs_bucket=f"memphis_police_data_lake_{project_id}", 
    spark_filename="spark_manipulations.py", 
    project_id=os.environ['PROJECT_ID'])

if __name__=='__main__':
    dataproc_flow()
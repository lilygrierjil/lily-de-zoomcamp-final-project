CREATE OR REPLACE EXTERNAL TABLE `final_project.external_memphis_police_data`
OPTIONS (
  format = 'parquet',
  uris = ['gs://prefect-de-zoomcamp-lily/data/memphis_police_data.parquet']
);

CREATE OR REPLACE TABLE final_project.memphis_police_data_partitioned_clustered
PARTITION BY DATE(offense_date_datetime)
CLUSTER BY category AS
SELECT * FROM final_project.external_memphis_police_data;
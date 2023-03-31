locals {
  data_lake_bucket = "memphis_police_data_lake"
  staging_bucket = "dataproc-staging-bucket"
  temp_bucket = "dataproc-temp-bucket"
}

variable "project" {
  description = "de-zoomcamp-final-project"
}

variable "region" {
  description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
  default = "us-central1"
  type = string
}

variable "storage_class" {
  description = "Storage class type for your bucket. Check official docs for more info."
  default = "STANDARD"
}

variable "BQ_DATASET" {
  description = "BigQuery Dataset that raw data (from GCS) will be written to"
  type = string
  default = "memphis_police_data_all"
}
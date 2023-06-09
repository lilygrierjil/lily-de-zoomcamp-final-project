# Memphis Police Data Processing Pipeline

For my capstone project for Data Engineering Zoomcamp 2023, I created an end-to-end data pipeline that makes calls to the Memphis City Data API.

## Problem Description

The city of Memphis, TN has an [open-source data hub]([url](https://data.memphistn.gov/)). 
Specifically, this project uses the [Public Safety Incidents dataset]([url](https://data.memphistn.gov/Public-Safety/Memphis-Police-Department-Public-Safety-Incidents/ybsi-jur4)) from the Memphis Police Department.
This dataset includes cases from 1986 to present and is updated daily.


It's important to note that police data doesn't give a complete picture of perceptions of safety. Due to [mistrust
of the police](https://www.urban.org/research/publication/mistrust-and-ambivalence-between-residents-and-police), people may refrain from calling the police when a safety threat comes along. 
Police may also use pretextual traffic stops, where they stop people for minor traffic violations that are not real
threats to safety in order to search them.
When advocating for criminal justice reform that emphasizes non-carceral ways of maintaining public safety, it's important to understand 
how the police are spending their time and what types of crimes are being committed. 


This project uses Memphis Police data to answer the following questions:

- How many crimes have been reported to police in Memphis, TN?
- What is the distribution of different crime categories (e.g., Motor Vehicle Theft, Assault, etc.)?

Because this is a large dataset that gets updated daily, this project also presents a batch processing solution to ingest the dataset each day. This allows for effective data processing and a regularly updated dashboard.


## About the Pipeline 

The pipeline uses the following technologies:
- Terraform to create Google Cloud resources through Infrastructure as Code
- Google Cloud Storage to serve as a data lake for storing raw data
- Google BigQuery to serve as a data warehouse where the data is prepared for analysis
- Google Compute Engine (hosts the GCP Virtual Machine)
- Google Dataproc Cluster for running PySpark queries to manipulate the data
- Prefect for pipeline orchestration and deployment
- Google Data Studio for dashboard creation

The pipeline consists of three Prefect flows, which are run as sub-flows in the full flow. 
- The first flow (found in `flows/ingest.py`) makes a call to the Memphis City Data API and downloads the most up-to-date dataset to a Google Cloud Storage data lake.


- The second flow (found in `flows/gcs_to_bq.py`) transfers the data from the data lake to BigQuery, a data warehouse tool. The data is partitioned on the month-year associated on which the offense date occurs and clustered on the 
category. Because it's a relatively small dataset (about 1.7 million rows with under 10 columns), I did not expect to see major gains from partitioning and clustering. I tested running the subsequent Spark queries with and without clustering and partitioning (i.e., clustered and partitioned, only clustered, only partitioned, neither clustered nor partitioned) and found that  clustering on crime categoy and partitioning on offense month resulted in some gains in query execution time (closer to 1 minute compared to 1 minute and 20 seconds). 

- The third and final flow (found in `flows/spark_job_flow.py`) transforms the data within the data warehouse and prepares it for the dashboard. The original dataset contains one row for each crime, and the query aggregates the dataset, grouping by crime type and month-year, to get monthly counts of crimes of each crime type.

After the full flow is run, we can use the aggregated dataset in Google Data Studio to create some visualizations to better understand the data.

## Dashboard

I created the following dashboard in Google Data Studio:
![image](images/Monthly_Crime_Type_Counts_Memphis_PD.png)

When looking at the breakdown of reported crime type categories, I found that assault and theft accounted for the majority of cases. The 2022 case counts show that crime generally increased as the year went on, though it did peak in the summer. Further analysis should explore whether the summer crime peak is consistent across years. We also see a high volume of cases attributed to vandalism and shoplifting misdeameanors. If it is found that these crimes don't impact public safety, it's worth investigating why police dedicate significant time and resources toward non-violent misdemeanor offenses.


You can play around with the dashboard [here](https://lookerstudio.google.com/s/rRvEdQZHnoM).

## Instructions for Replication

To replicate this project, you'll need a Google Cloud Platform account. GCP offers a 30-day free trial. 

1. If you don't already have a VM, create one in the GCP console. I recommend using a 
e2-custom-2-10240 machine type with 
x86/64 architecture.
2. Clone this repository using the command: `git clone https://github.com/lilygrierjil/lily-de-zoomcamp-final-project.git`. Perform the following commands in the root of this repository.

2. Install the gcloud CLI following [these instructions](https://cloud.google.com/sdk/docs/install-sdk#installing_the_latest_version).

3. Create a new project (I'll call it de-zoomcamp-final-project, but it doesn't matter what you call it so long as it's a globally unique project ID) and link it to a billing account using the following commands:

```
gcloud projects create <PROJECT_ID>

# Set the correct project variable
gcloud config set project <PROJECT_ID>

# Display list of billing accounts
gcloud alpha billing accounts list

# Link new project to billing account
gcloud beta billing projects link <PROJECT_ID> \
  --billing-account=<INSERT_BILLING_ACCOUNT_ID>
  

# export the project id to your environment
export PROJECT_ID=$(gcloud config get-value project)

# export the project ID as terraform var
export TF_VAR_project=$PROJECT_ID

```

4. Create a service account with the appropriate roles by running the following commands:
```
chmod +x setup.sh
./setup.sh
```
This script creates a service account named terraform and assigns it the appropriate roles.
The credentials for this service account are stored in a file called `service_account.json` that gets stored
in the root of the repo.

5. If you don't already have terraform on your VM, follow [these directions](https://github.com/robertpeteuil/terraform-installer#download-and-use-locally) to install terraform to your VM.

6. Run the following commands to use terraform to create the remaining resources:
```
terraform init

# Check changes to new infra plan
terraform plan -var="project=$PROJECT_ID"
# Create new infra
terraform apply -var="project=$PROJECT_ID"
```

7. Activate the environment by running `conda env update -n finalproject -f environment.yml` followed by `conda activate finalproject`.

7. To run the full ETL, open one additional terminal window, run `conda activate finalproject`, and run `prefect orion start`. Then open a second window, run `conda activate finalproject`, and run `prefect agent start --work-queue "default"`. 


9. Run python `deployment.py` to create the deployments. This creates two deployments, one to be run on a daily schedule and one that can be called ad hoc. 

9. To run the pipeline immediately, run `prefect deployment run main-flow/one-time-deployment`. The command will output a URL on which you can view the flow's progress via the Prefect GUI. Note that the pipeline takes 15-ish minutes to run in full. 

99. When you are done, be sure to run `terraform destroy` to destroy all created resources. This step is important as the project uses resource-intensive services that could end up costing you money if you don't shut them down! 


## Future Considerations

Future iterations of this project may consider:
 - using a Docker container to run the prefect agent and orion server in the background so the user doesn't have to boot those up manually
 - implementing CI/CD so the whole pipeline runs automatically
 - having functionality to download the full dataset one time, then on subsequent runs only download data that's been added since the last run
 - incorporating other datasets into the project for comparison (e.g., number of Memphis police officers over time, census demographic information, employment statistics, etc.)


# Create the service account
gcloud iam service-accounts create terraform \
  --description="Service Account to use with Terraform"

# Create the key file
gcloud iam service-accounts keys create service_account.json \
  --iam-account=terraform@$PROJECT_ID.iam.gserviceaccount.com

export GOOGLE_APPLICATION_CREDENTIALS="service_account.json"


# Grant the Editor role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:terraform@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/editor

# Grant the Security Admin role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:terraform@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/iam.securityAdmin

# grant storage admin

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:terraform@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/storage.admin


# grant big query admin

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:terraform@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/bigquery.admin


# grant storage object admin

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:terraform@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/storage.objectAdmin

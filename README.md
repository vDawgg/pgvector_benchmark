## Setup for running on GCE

Install the gcloud cli and authenticate for the first time. When asked for a passphrase for the ssh file, leave this blank, as this will get annoying pretty quickly otherwise.

The project is currently set up, so the trace data is gathered from a gcs bucket before the benchmark is executed.
This is done to ensure that the benchmark can be executed in a timely manner, as the trace data is ~35GB in size and uploading this everytime might be prohibitively slow depending on your upload speed.
To do this, first add a new storage bucket to your project and upload a gzipped version of the trace directory. Then grant access to this bucket to 
the default project account by running:

```shell
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:<SERVICE_ACCOUNT_EMAIL>" \
  --role="roles/storage.objectViewer"
```


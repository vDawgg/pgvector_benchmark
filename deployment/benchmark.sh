client_name="pgvector-client"
zone="europe-west3-c"

# Deploy terraform configuration
terraform apply -auto-approve

# TODO: It is probably a better idea to just clone the project and then only copy the data needed over to the machine.
# Copy the project dir to the client instance
gcloud compute scp ../* $client_name:~/. --zone $zone

# Get the client instances IP addr
SUT_IP="$(gcloud compute instances describe $SUTinstanceName --zone='europe-west3-c' --format='get(networkInterfaces[0].accessConfigs[0].natIP)')"

# Set up the project on the client instance
gcloud compute ssh $client_name --zone $zone "sh ./deployment/run_bench_client.sh" $SUT_IP
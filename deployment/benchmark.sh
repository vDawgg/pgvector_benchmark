RUN=$1
REQUESTS_PER_SECOND=$2
INDEXING_METHOD=$3
CLIENT_INSTANCE_NAME="pgvector-client-$RUN"
SUT_INSTANCE_NAME="pgvector-sut-$RUN"
ZONE="europe-west3-c"
PROJECT_ID=benchmark-446021

# Deploy terraform configuration
terraform apply -var="run-number=$RUN" -var="project-id=$PROJECT_ID" -auto-approve

# Sleep for 10 seconds to make sure that the instances are reachable
sleep 10

# Check for startup_script completion on client instance
while true; do
  if gcloud compute ssh "$CLIENT_INSTANCE_NAME" \
      --project="$PROJECT_ID" \
      --zone="$ZONE" \
      --tunnel-through-iap \
      --command="test -f /done" 2>/dev/null; then
    break
  else
    sleep 5
  fi
done

# Get the client instances IP addr
SUT_IP="$(gcloud compute instances describe $SUT_INSTANCE_NAME --project $PROJECT_ID --zone $ZONE --format='get(networkInterfaces[0].networkIP)')"

# Set up and run the project on the client instance
gcloud compute ssh $CLIENT_INSTANCE_NAME --project $PROJECT_ID --zone $ZONE --tunnel-through-iap --command "sudo sh /pgvector_benchmark/deployment/run_bench_client.sh $SUT_IP $RUN $REQUESTS_PER_SECOND $INDEXING_METHOD"

# Copy the results from the client instance
gcloud compute scp --project $PROJECT_ID --tunnel-through-iap --zone $ZONE $CLIENT_INSTANCE_NAME:/pgvector_benchmark/benchmark/results/* ../benchmark/results

# Destroy the resources
terraform destroy -var="run-number=$RUN" -var="project-id=$PROJECT_ID" -auto-approve

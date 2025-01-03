INSTANCE_NAME="pgvector-client"
ZONE="europe-west3-c"
PROJECT_ID=benchmark-446021

# Deploy terraform configuration
terraform apply -auto-approve

# Sleep for 10 seconds to make sure that the instances are reachable
sleep 10

# Check for startup_script completion on client instance
while true; do
  if gcloud compute ssh "$INSTANCE_NAME" \
      --project="$PROJECT_ID" \
      --zone="$ZONE" \
      --command="test -f /done" 2>/dev/null; then
    break
  else
    sleep 5
  fi
done

# Get the client instances IP addr
SUT_IP="$(gcloud compute instances describe $INSTANCE_NAME --project $PROJECT_ID --zone $ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)')"

# Set up and run the project on the client instance
gcloud compute ssh $INSTANCE_NAME --project $PROJECT_ID --zone $ZONE --command "sh ~/pgvector_benchmark/deployment/run_bench_client.sh $SUT_IP"

# Wait for benchmark to finish
while true; do
  if gcloud compute ssh "$INSTANCE_NAME" \
      --project="$PROJECT_ID" \
      --zone="$ZONE" \
      --command="test -f /pgvector_benchmark/benchmark/results/query_log.pkl" 2>/dev/null; then
    break
  else
    sleep 300
  fi
done

# Copy the results from the client instance
gcloud compute scp --project $PROJECT_ID --zone $ZONE $INSTANCE_NAME:/pgvector_benchmark/benchmark/results/* ../benchmark/results

# Destroy the resources
terraform destroy -auto-approve
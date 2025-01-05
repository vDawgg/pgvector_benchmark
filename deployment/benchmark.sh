CLIENT_INSTANCE_NAME="pgvector-client"
SUT_INSTANCE_NAME="pgvector-sut"
ZONE="europe-west3-c"
PROJECT_ID=benchmark-446021

# Deploy terraform configuration
terraform apply -auto-approve

# Sleep for 10 seconds to make sure that the instances are reachable
sleep 10

# Check for startup_script completion on client instance
while true; do
  if gcloud compute ssh "$SUT_INSTANCE_NAME" \
      --project="$PROJECT_ID" \
      --zone="$ZONE" \
      --command="test -f /done" 2>/dev/null; then
    break
  else
    sleep 5
  fi
done

# Get the client instances IP addr and ID
SUT_IP="$(gcloud compute instances describe $SUT_INSTANCE_NAME --project $PROJECT_ID --zone $ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)')"
SUT_ID="$(gcloud compute instances describe $SUT_INSTANCE_NAME --format="get(id)")"

# Define starting time for the benchmark
BENCH_START_TIME="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

# Set up and run the project on the client instance
gcloud compute ssh $CLIENT_INSTANCE_NAME --project $PROJECT_ID --zone $ZONE --command "sudo sh /pgvector_benchmark/deployment/run_bench_client.sh $SUT_IP"

# Wait for benchmark to finish
while true; do
  if gcloud compute ssh "$CLIENT_INSTANCE_NAME" \
      --project="$PROJECT_ID" \
      --zone="$ZONE" \
      --command="test -f /pgvector_benchmark/benchmark/results/query_log.pkl" 2>/dev/null; then
    break
  else
    sleep 300
  fi
done

# Copy the results from the client instance
gcloud compute scp --project $PROJECT_ID --zone $ZONE $CLIENT_INSTANCE_NAME:/pgvector_benchmark/benchmark/results/* ../benchmark/results
gcloud compute scp --project $PROJECT_ID --zone $ZONE $SUT_INSTANCE_NAME:/tmp/sut_resource_usage.csv ..benchmark/results

# Get the resource usage from the SUT instance
gcloud monitoring time-series list \
  --project=$PROJECT_ID \
  --filter="metric.type='compute.googleapis.com/instance/cpu/utilization'
            AND resource.labels.instance_id='$SUT_ID'" \
  --interval="$BENCH_START_TIME,end=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --format="csv(points.interval.endTime, points.value.doubleValue)" > ../benchmark/results/cpu_util.csv
gcloud monitoring time-series list \
  --project=$PROJECT_ID \
  --filter="metric.type='agent.googleapis.com/memory/percent_used'
            AND resource.labels.instance_id='$SUT_ID'" \
  --interval="start=$BENCH_START_TIME,end=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --format="csv(points.interval.endTime, points.value.doubleValue)" > ../benchmark/results/mem_util.csv

# Destroy the resources
terraform destroy -auto-approve
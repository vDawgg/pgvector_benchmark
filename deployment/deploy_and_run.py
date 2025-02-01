import argparse
import subprocess
from time import sleep

from env import PROJECT_ID, REGION, ZONE

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--indexing_method",
        help="Indexing method",
        default="",
        choices=["ivfflat", "hnsw"],
    )
    parser.add_argument(
        "--requests_per_second",
        help="Average number of requests per second",
        type=int,
        required=True
    )
    parser.add_argument(
        "--run_number",
        help="Run number",
        type=int,
        required=True
    )
    args = parser.parse_args()
    args = vars(args)

    indexing_method = args.pop("indexing_method")
    requests_per_second = args.pop("requests_per_second")
    run_number = args.pop("run_number")

    client_instance_name = f"pgvector-client-{indexing_method}-{run_number}"
    sut_instance_name = f"pgvector-sut-{indexing_method}-{run_number}"

    subprocess.run(f"terraform workspace new {indexing_method}_{run_number}", shell=True)
    subprocess.run(f"terraform workspace select {indexing_method}_{run_number}", shell=True)

    print("Deploying infrastructure")
    subprocess.run(f'terraform apply -var="indexing_method={indexing_method}" -var="run_number={run_number}" -var="project_id={PROJECT_ID}" -var="region={REGION}" -var="zone={ZONE}" -auto-approve', shell=True)

    #sleep(10)
    
    while True:
        res = subprocess.run(
            f"gcloud compute ssh {client_instance_name} --project={PROJECT_ID} --zone={ZONE} --tunnel-through-iap --command='test -f /done' 2>/dev/null",
            stdout=subprocess.DEVNULL,
            shell=True,
        )
        if res.returncode == 0:
            break
        sleep(5)

    print("Deployment finished")

    sut_ip = subprocess.run(f'gcloud compute instances describe {sut_instance_name} --project={PROJECT_ID} --zone={ZONE} --format="get(networkInterfaces[0].networkIP)"', shell=True)

    print("Starting benchmark run")
    subprocess.run(
        f"gcloud compute ssh {client_instance_name} --project={PROJECT_ID} --zone={ZONE} --tunnel-through-iap --ssh-flag='-t' --command='sudo sh /pgvector_benchmark/deployment/run_bench_client.sh $SUT_IP {run_number} {requests_per_second} {indexing_method}'",
        shell=True
    )

    while True:
        res = subprocess.run(
            f"gcloud compute ssh {client_instance_name} --project={PROJECT_ID} --zone={ZONE} --tunnel-through-iap --command='compgen -G /pgvector_benchmark/benchmark/results/*.pkl 2>/dev/null'",
            shell=True,
            stdout=subprocess.DEVNULL,
        )
        if res.returncode == 0:
            break
        sleep(600)

    print("Benchmark finished, copying results")
    subprocess.run(
        f"gcloud compute scp --project={PROJECT_ID} --zone={ZONE} --tunnel-through-iap {client_instance_name}:/pgvector_benchmark/benchmark/results/* ..benchmark/results",
        shell=True
    )

    print("Destroying resources")
    subprocess.run(f"terraform workspace select {indexing_method}_{run_number}", shell=True)
    subprocess.run(f'terraform destroy -var="indexing_method={indexing_method}" -var="run_number={run_number}" -var="project_id={PROJECT_ID}" -var="region={REGION}" -var="zone={ZONE}" -auto-approve', shell=True)
    print("DONE")

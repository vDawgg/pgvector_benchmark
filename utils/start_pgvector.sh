docker container stop $(docker container ls -aq) && docker system prune -af --volumes
docker pull pgvector/pgvector:pg17
IMAGE_ID="$(docker images --format "{{.ID}}")"
docker run --memory="8g" --memory-swap="8g" --cpus="4" --name pgvector -e POSTGRES_PASSWORD=123 -p 5432:5432 "$IMAGE_ID" \
-c max_connections=500 -c shared_buffers=2GB -c effective_cache_size=6GB -c maintenance_work_mem=512MB -c checkpoint_completion_target=0.9 \
-c wal_buffers=16MB -c default_statistics_target=100 -c random_page_cost=1.1 -c effective_io_concurrency=200 -c work_mem=524kB \
-c huge_pages=off -c min_wal_size=1GB -c max_wal_size=4GB -c max_worker_processes=8 -c max_parallel_workers_per_gather=4 \
-c max_parallel_workers=8 -c max_parallel_maintenance_workers=4

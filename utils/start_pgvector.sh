docker container stop $(docker container ls -aq) && docker system prune -af --volumes
docker pull pgvector/pgvector:pg17
IMAGE_ID="$(docker images --format "{{.ID}}")"
docker run --memory="8g" --memory-swap="8g" --cpus="4" --name pgvector -e POSTGRES_PASSWORD=123 -d -p 5432:5432 "$IMAGE_ID"
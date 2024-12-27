docker container stop $(docker container ls -aq) && docker system prune -af --volumes
docker pull pgvector/pgvector:pg17
docker run --memory="8g" --memory-swap="8g" --cpus="4" --name pgvector -e POSTGRES_PASSWORD=123 -d -p 5432:5432 206f8e0dc14e
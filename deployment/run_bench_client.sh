cd /
gsutil cp gs://bench-data-bucket/trace.tar.gz ./pgvector_benchmark/benchmark
tar -xvf ./pgvector_benchmark/benchmark/trace.tar.gz -C ./pgvector_benchmark/benchmark
cd ./pgvector_benchmark
python3 -m pip install -r requirements.txt
python3 main.py $1
cd /pgvector_benchmark

gsutil gs://bench-data-bucket/trace.tar.gz /pgvector_benchmark/benchmark

tar -xvf /pgvector_benchmark/benchmark/trace.tar.gz /pgvector_benchmark/benchmark/trace

pip install -r requirements.txt

python main.py $1
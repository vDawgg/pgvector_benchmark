cd ~

cd ~/pgvector_benchmark

sudo gsutil cp gs://bench-data-bucket/trace.tar.gz ~/pgvector_benchmark/benchmark

sudo tar -xvf ~/pgvector_benchmark/benchmark/trace.tar.gz -C ~/pgvector_benchmark/benchmark

python3 -m pip install -r requirements.txt

python3 main.py $1
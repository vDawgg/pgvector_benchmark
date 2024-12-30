#Autostart services https://askubuntu.com/questions/1367139/apt-get-upgrade-auto-restart-services
export DEBIAN_FRONTEND=noninteractive

sudo apt update
sudo apt upgrade -y
sudo apt install git

git clone https://github.com/vDawgg/pgvector_benchmark

touch /done
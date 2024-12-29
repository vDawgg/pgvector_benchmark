#Autostart services https://askubuntu.com/questions/1367139/apt-get-upgrade-auto-restart-services
export DEBIAN_FRONTEND=noninteractive

sudo apt update
sudo apt upgrade -y
sudo apt install -y -q apt-transport-https ca-certificates curl software-properties-common # TODO: Check if this is necessary
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository --yes "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
sudo apt update
sudo apt upgrade -y
sudo apt install -y -q docker-ce

sudo service docker-ce start
sudo docker pull pgvector/pgvector:pg17
sudo docker run --name pgvector -e POSTGRES_PASSWORD=123 -d -p 5432:5432 206f8e0dc14e # TODO: Think about adding resource constraints here and parameterizing the password

touch /done
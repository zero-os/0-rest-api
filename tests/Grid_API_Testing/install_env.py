branch=$1
zerotierid=$2
zerotiertoken=$3

export SSHKEYNAME=id_rsa
export GIGBRANCH=master
export GIGSAFE=1
export TERM=xterm-256color

## generate ssh key
echo "[#] Generate SSH key ..."
ssh-keygen -f $HOME/.ssh/id_rsa -t rsa -N ''

#install requirments
sudo apt-get update
sudo apt-get install python3-pip -y
sudo apt-get install python3-dev -y
sudo apt-get install libffi-dev -y
sudo apt-get install python3-pip -y
sudo pip3 install paramiko
sudo pip3 install configargparse
sudo pip3 install -U git+https://github.com/zero-os/0-orchestrator.git#subdirectory=pyclient
sudo pip3 install -U git+https://github.com/zero-os/0-core.git#subdirectory=client/py-client

## install docker-ce
echo "[#] Installing docker ..."
sudo apt-get -y install \
apt-transport-https \
ca-certificates \
curl
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
"deb [arch=amd64] https://download.docker.com/linux/ubuntu \
$(lsb_release -cs) \
stable"
sudo apt-get update
sudo apt-get -y install docker-ce

## install zerotier in packet machine 
echo "[#] Installing Zerotier ..."
curl -s https://install.zerotier.com/ | sudo bash

## install Jumpscale 9
echo "[#] Installing Jumpscale 9 ..."
curl -s https://raw.githubusercontent.com/Jumpscale/developer/master/jsinit.sh | bash
source ~/.jsenv.sh 

js9_build -l

## start js9 docker
echo "[#] Starting JS9 container ..."
js9_start 

## make local machine join zerotier network
echo "[#] Joining zerotier network (local machine) ..."
sudo zerotier-one -d || true
sleep 5

sudo zerotier-cli join ${zerotierid}
sleep 5

## authorized local machine as zerotier member
echo "[#] Authorizing zerotier member ..."
memberid=$(sudo zerotier-cli info | awk '{print $3}')
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${zerotiertoken}" -X POST -d '{"config": {"authorized": true}}' https://my.zerotier.com/api/network/${zerotierid}/member/${memberid}

## make js9 container join zerotier network
echo "[#] Joining zerotier network (js9 container) ..."
docker exec -d js9 bash -c "zerotier-one -d" || true
sleep 5

docker exec js9 bash -c "zerotier-cli join ${zerotierid}"
sleep 5 

## authorized js9 container as zerotier member
echo "[#] Authorizing zerotier member ..."
memberid=$(docker exec js9 bash -c "zerotier-cli info" | awk '{print $3}')
curl -H "Content-Type: application/json" -H "Authorization: Bearer ${zerotiertoken}" -X POST -d '{"config": {"authorized": true}}' https://my.zerotier.com/api/network/${zerotierid}/member/${memberid}
sleep 5 

## install orchestrator
echo "[#] Installing orchestrator ..."
ssh -tA root@localhost -p 2222 "export GIGDIR=~/gig; curl -sL https://raw.githubusercontent.com/ahmedelsayed-93/0-orchestrator/perf_jenkins_project/scripts/install-orchestrator.sh | bash -s ${branch} ${zerotierid} ${zerotiertoken}"
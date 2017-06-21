#!/bin/bash


error_handler() {
    EXITCODE=$?

    if [ -z $2 ]; then
        echo "[-] line $1: unexpected error"
        exit ${EXITCODE}
    else
        echo $2
    fi

    exit 1
}

trap 'error_handler $LINENO' ERR

export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

logfile="/tmp/install.log"

if [ -z $1 ] || [ -z $2 ] || [ -s $3 ]; then
  echo "Usage: installgrid.sh <BRANCH> <ZEROTIERNWID> <ZEROTIERTOKEN> <ITSYOUONLINEORG> <CLIENTSECRET> [<DOMAIN> [--development]]"
  echo
  echo "  BRANCH: 0-orchestrator development branch."
  echo "  ZEROTIERNWID: Zerotier network id."
  echo "  ZEROTIERTOKEN: Zerotier api token."
  echo "  ITSYOUONLINEORG: itsyou.online organization for use to authenticate."
  echo "  CLIENTSECRET: client secret for itsyou.online authentication."
  echo "  DOMAIN: the domain to use for caddy."
  echo "  --development: an optional parameter to use self signed certificates."
  echo
  exit 1
fi
BRANCH=$1
shift
ZEROTIERNWID=$1
shift
ZEROTIERTOKEN=$1
shift
ITSYOUONLINEORG=$1
shift
CLIENTSECRET=$1
shift
DOMAIN=$1

if [ -n "$DOMAIN" ]; then
    shift
    if [ "$1" = "--development" ]; then
        DEVELOPMENT=true
        shift
    else
        DEVELOPMENT=false
    fi
else
    DEVELOPMENT=true
fi

# NOTE that you can't add any arguments after here, if you want to do so, please use argparse

CODEDIR="/root/gig/code"
if [ "$GIGDIR" != "" ]; then
    CODEDIR="$GIGDIR/code"
fi

echo "[+] Configuring zerotier"
mkdir -p /etc/my_init.d > ${logfile} 2>&1
ztinit="/etc/my_init.d/10_zerotier.sh"

echo '#!/bin/bash -x' > ${ztinit}
echo 'zerotier-one -d' >> ${ztinit}
echo 'while ! zerotier-cli info > /dev/null 2>&1; do sleep 0.1; done' >> ${ztinit}
echo "[ $ZEROTIERNWID != \"\" ] && zerotier-cli join $ZEROTIERNWID" >> ${ztinit}

chmod +x ${ztinit} >> ${logfile} 2>&1
bash $ztinit >> ${logfile} 2>&1

echo "[+] Waiting for zerotier connectivity"
if ! zerotier-cli listnetworks | egrep -q 'OK PRIVATE|OK PUBLIC'; then
    echo "[-] ZeroTier interface zt0 does not have an ipaddress."
    echo "[-] Make sure you authorized this docker into your ZeroTier network"
    echo "[-] ZeroTier Network ID: ${ZEROTIERNWID}"

    while ! zerotier-cli listnetworks | egrep -q 'OK PRIVATE|OK PUBLIC'; do
        sleep 0.2
    done
fi

echo "[+] Installing orchestrator dependencies"
pip3 install -U "git+https://github.com/zero-os/0-core.git@${BRANCH}#subdirectory=client/py-client" >> ${logfile} 2>&1
pip3 install -U "git+https://github.com/zero-os/0-orchestrator.git@${BRANCH}#subdirectory=pyclient" >> ${logfile} 2>&1
pip3 install -U zerotier >> ${logfile} 2>&1
python3 -c "from js9 import j; j.tools.prefab.local.development.golang.install()" >> ${logfile} 2>&1
mkdir -p /usr/local/go >> ${logfile} 2>&1

echo "[+] Updating AYS orchestrator server"
mkdir -p $CODEDIR/github >> ${logfile} 2>&1
pushd $CODEDIR/github
mkdir -p zero-os >> ${logfile} 2>&1
pushd zero-os

if [ ! -d "0-orchestrator" ]; then
    git clone https://github.com/zero-os/0-orchestrator.git >> ${logfile} 2>&1
fi
pushd 0-orchestrator
git pull
git checkout ${BRANCH} >> ${logfile} 2>&1
popd

if [ ! -d "0-core" ]; then
    git clone https://github.com/zero-os/0-core.git >> ${logfile} 2>&1
fi
pushd 0-core
git pull
git checkout ${BRANCH} >> ${logfile} 2>&1
popd

echo "[+] Start AtYourService server"

aysinit="/etc/my_init.d/10_ays.sh"
if [ -n "${ITSYOUONLINEORG}" ]; then
    if [ ! -d /optvar/cfg/ ]; then
        mkdir /optvar/cfg/
    fi
    cat >  /optvar/cfg/jumpscale9.toml << EOL
[ays]
production = true

[ays.oauth]
client_secret = "${CLIENTSECRET}"
jwt_key = "MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAES5X8XrfKdx9gYayFITc89wad4usrk0n27MjiGYvqalizeSWTHEpnd7oea9IQ8T5oJjMVH5cc0H5tFSKilFFeh//wngxIyny66+Vq5t5B0V0Ehy01+2ceEon2Y0XDkIKv"
organization = "${ITSYOUONLINEORG}"
EOL
fi

echo '#!/bin/bash -x' > ${aysinit}
echo 'ays start > /dev/null 2>&1' >> ${aysinit}

chmod +x ${aysinit} >> ${logfile} 2>&1
bash $aysinit >> ${logfile} 2>&1

echo "[+] Waiting for AtYourService"
while ! curl http://127.0.0.1:5000 >> ${logfile} 2>&1; do sleep 0.1; done

echo "[+] Building orchestrator api server"
mkdir -p /opt/go/proj/src/github.com >> ${logfile} 2>&1
if [ ! -d /opt/go/proj/src/github.com/zero-os ]; then
    ln -sf ${CODEDIR}/github/zero-os /opt/go/proj/src/github.com/zero-os >> ${logfile} 2>&1
fi
cd /opt/go/proj/src/github.com/zero-os/0-orchestrator/api
GOPATH=/opt/jumpscale9/go/proj GOROOT=/opt/jumpscale9/go/root /opt/jumpscale9/go/root/bin/go build -o /usr/local/bin/orchestratorapiserver >> ${logfile} 2>&1
if [ ! -d /optvar/cockpit_repos/orchestrator-server ]; then
    mkdir -p /optvar/cockpit_repos/orchestrator-server >> ${logfile} 2>&1
    mkdir -p /optvar/cockpit_repos/orchestrator-server/services >> ${logfile} 2>&1
    mkdir -p /optvar/cockpit_repos/orchestrator-server/actorTemplates >> ${logfile} 2>&1
    mkdir -p /optvar/cockpit_repos/orchestrator-server/actors >> ${logfile} 2>&1
    mkdir -p /optvar/cockpit_repos/orchestrator-server/blueprints >> ${logfile} 2>&1
    touch /optvar/cockpit_repos/orchestrator-server/.ays >> ${logfile} 2>&1
    git init /optvar/cockpit_repos/orchestrator-server >> ${logfile} 2>&1
fi

echo "[+] Starting orchestrator api server"
orchinit="/etc/my_init.d/11_orchestrator.sh"
ZEROTIERIP=`ip -4 addr show zt0 | grep -oP 'inet\s\d+(\.\d+){3}' | sed 's/inet //' | tr -d '\n\r'`
if [ "$ZEROTIERIP" == "" ]; then
    echo "zerotier doesn't have an ip. make sure you have authorize this docker in your netowrk"
    exit 1
fi

if [ -z "$DOMAIN" ]; then
    PRIV="$ZEROTIERIP"
    PUB="https://$ZEROTIERIP:443/"
else
    PRIV="127.0.0.1"
    PUB="https://$DOMAIN:443/"
fi


# create orchestrator service
echo '#!/bin/bash -x' > ${orchinit}
if [ -z "${ITSYOUONLINEORG}" ]; then
    echo 'cmd="orchestratorapiserver --bind '"${PRIV}"':8080 --ays-url http://127.0.0.1:5000 --ays-repo orchestrator-server "' >> ${orchinit}
else
    echo 'cmd="orchestratorapiserver --bind '"${PRIV}"':8080 --ays-url http://127.0.0.1:5000 --ays-repo orchestrator-server --org '"${ITSYOUONLINEORG}"'"' >> ${orchinit}
fi

echo 'tmux new-session -d -s main -n 1 || true' >> ${orchinit}
echo 'tmux new-window -t main -n orchestrator' >> ${orchinit}
echo 'tmux send-key -t orchestrator.0 "$cmd" ENTER' >> ${orchinit}

js9 'j.tools.prefab.local.apps.caddy.install()'
tls=
if [ "$DEVELOPMENT" = true ]; then
    tls='tls self_signed'
fi

cfgdir=`js9 "print(j.dirs.CFGDIR)"`
cat > $cfgdir/caddy.cfg <<EOF
#tcpport:443
$PUB {
    proxy / $PRIV:8080 {
        transparent
    }
    $tls
}
EOF
echo 'js9 "j.tools.prefab.local.apps.caddy.start()"' >> ${orchinit}


chmod +x ${orchinit} >> ${logfile} 2>&1
bash $orchinit >> ${logfile} 2>&1

echo "[+] Deploying bootstrap service"
echo -e "bootstrap.zero-os__grid1:\n  zerotierNetID: '"${ZEROTIERNWID}"'\n  zerotierToken: '"${ZEROTIERTOKEN}"'\n\nactions:\n  - action: install\n" > /optvar/cockpit_repos/orchestrator-server/blueprints/bootstrap.bp
cd /optvar/cockpit_repos/orchestrator-server; ays blueprint >> ${logfile} 2>&1
cd /optvar/cockpit_repos/orchestrator-server; ays run create --follow -y >> ${logfile} 2>&1

echo "Your ays server is ready to bootstrap nodes into your zerotier network."
if [ -z "${ITSYOUONLINEORG}" ]; then
    echo "Download your ipxe boot iso image https://bootstrap.gig.tech/iso/${BRANCH}/${ZEROTIERNWID}/ and boot up your nodes!"
else
    echo "Download your ipxe boot iso image https://bootstrap.gig.tech/iso/${BRANCH}/${ZEROTIERNWID}/organization=${ITSYOUONLINEORG} and boot up your nodes!"
fi
echo "Enjoy your orchestrator api server: $PUB"

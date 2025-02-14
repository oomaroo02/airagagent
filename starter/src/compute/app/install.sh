#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

. ./env.sh

# Python 
sudo dnf install -y python39 python39-devel wget

# Anonymize
sudo dnf install -y poppler-utils mesa-libGL

sudo pip3.9 install pip --upgrade
pip3.9 install -r requirements.txt

# PDFKIT
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.centos8.x86_64.rpm
sudo dnf localinstall -y wkhtmltox-0.12.6-1.centos8.x86_64.rpm
mv *.rpm /tmp

# LibreOffice (convert docx to PDF)
if [ "${INSTALL_LIBREOFFICE}" != "" ]; then
    cd /tmp
    export LIBREOFFICE_VERSION=$INSTALL_LIBREOFFICE
    wget https://download.documentfoundation.org/libreoffice/stable/${LIBREOFFICE_VERSION}/rpm/x86_64/LibreOffice_${LIBREOFFICE_VERSION}_Linux_x86-64_rpm.tar.gz
    tar -xzvf LibreOffice_${LIBREOFFICE_VERSION}_Linux_x86-64_rpm.tar.gz
    cd LibreOffice*/RPMS
    sudo dnf install *.rpm -y
    libreoffice24.8 --version
fi 

# Chrome + Selenium to get webpage
if [ "${INSTALL_CHROME}" != "" ]; then
   cd /tmp
   wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
   sudo dnf localinstall -y google-chrome-stable_current_x86_64.rpm
fi 
cd $SCRIPT_DIR

# Store the config in APEX
export TNS_ADMIN=$HOME/db
$HOME/db/sqlcl/bin/sql $DB_USER/$DB_PASSWORD@DB <<EOF
begin
  update APEX_APP.AI_AGENT_RAG_CONFIG set value='$AGENT_ENDPOINT_OCID' where key='agent_endpoint';
  commit;
end;
/
exit;
EOF

# Get COMPARTMENT_OCID
curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/ > /tmp/instance.json
export TF_VAR_compartment_ocid=`cat /tmp/instance.json | jq -r .compartmentId`

# Create services
create_service () {
    APP_DIR=$1
    COMMAND=$2
    # Create an db service
    cat > /tmp/$COMMAND.service << EOT
[Unit]
Description=$COMMAND
After=network.target

[Service]
Type=simple
ExecStart=/home/opc/$APP_DIR/${COMMAND}.sh
TimeoutStartSec=0
User=opc

[Install]
WantedBy=default.target
EOT
    sudo cp /tmp/$COMMAND.service /etc/systemd/system
    sudo chmod 664 /etc/systemd/system/$COMMAND.service
    sudo systemctl daemon-reload
    sudo systemctl enable $COMMAND.service
    sudo systemctl restart $COMMAND.service
}

create_service app ingest
create_service app streamlit
create_service app tools

sudo firewall-cmd --zone=public --add-port=8081/tcp --permanent


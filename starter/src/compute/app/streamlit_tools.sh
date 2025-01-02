#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

. ./env.sh

streamlit run streamlit_tools.py --server.port 8080 2>&1 | tee streamlit_tools.log

# Ex: curl "http://$BASTION_IP:8080/"

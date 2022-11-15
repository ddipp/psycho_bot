#!/bin/bash

rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip3 install -U pip
pip3 install -U setuptools
pip3 install -r requirements.dev.txt
source enviroment.sh
pip3 freeze > requirements.txt

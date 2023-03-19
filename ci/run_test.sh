#!/usr/bin/env bash
set -e
set -x

python3 -m pip install -r requirements.txt

python3 -m unittest discover -s test -p "*test.py"
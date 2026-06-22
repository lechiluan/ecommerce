#!/usr/bin/env bash
set -o errexit

python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python manage.py collectstatic --no-input --clear
python manage.py migrate

#!/bin/bash

cd biblioteca

pip3 install -r requirements.txt

python3 manage.py migrate
python3 manage.py collectstatic --noinput

PORT=${PORT:-8000}

python3 manage.py runserver 0.0.0.0:$PORT
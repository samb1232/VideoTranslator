# flask_api/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./shared_utils ./shared_utils
COPY ./database ./database
COPY ./config.py ./app.py ./routes.py ./rabbitmq_workers.py ./logging_conf.py ./users.json ./wait-for-it.sh ./

EXPOSE 5000

# TODO: изменить настройки gunicorn
CMD [\
    "./wait-for-it.sh", \
    "rabbitmq:5672", "--", \
    "gunicorn", \
    "-w 1", \
    "-b :5000", \
    "app:app"] 

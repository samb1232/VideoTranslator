# speech_to_text/Dockerfile
FROM python:3.11-slim

# Install necessary dependencies for building mysqlclient and ffmpeg
RUN apt-get update && apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./shared_utils ./shared_utils
COPY ./utils ./utils
COPY ./.env ./config_rabbitmq.py ./rabbitmq_subs_gen_worker.py ./subs_generator.py ./subs_translator.py ./logging_conf.py ./wait-for-it.sh ./


CMD ["./wait-for-it.sh", "rabbitmq:5672", "--", "python", "rabbitmq_subs_gen_worker.py"] 

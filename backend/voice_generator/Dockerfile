# text_to_speech/Dockerfile
FROM python:3.11-slim

# Install necessary dependencies for building mysqlclient and ffmpeg
RUN apt-get update && apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./tts_models/tts_models--multilingual--multi-dataset--xtts_v2 /root/.local/share/tts/tts_models--multilingual--multi-dataset--xtts_v2
COPY ./utils ./utils
COPY ./config.py ./rabbitmq_voice_gen_worker.py ./voice_generator.py ./logging_conf.py ./wait-for-it.sh ./

CMD ["./wait-for-it.sh", "rabbitmq:5672", "--", "python", "rabbitmq_voice_gen_worker.py"] 

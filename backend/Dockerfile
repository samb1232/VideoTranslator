# backend/Dockerfile
FROM python:3.11-slim

# Install necessary dependencies for building mysqlclient and ffmpeg
RUN apt-get update && apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./modules/tts_models/tts_models--multilingual--multi-dataset--xtts_v2 /root/.local/share/tts/tts_models--multilingual--multi-dataset--xtts_v2
COPY ./database ./database
COPY ./modules ./modules
COPY ./resources ./resources
COPY ./config.py ./web_server.py ./users.json ./

ENV FLASK_ENV production

EXPOSE 5000

CMD ["gunicorn", "-b", ":5000", "-t 0", "web_server:app"]

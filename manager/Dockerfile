FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    cron \
    curl \
    mc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app/. .
RUN pip install -r requirements.txt

RUN chmod +x *.py

COPY my_cron /etc/cron.d/my_cron

RUN chmod 0644 /etc/cron.d/my_cron \
    && crontab /etc/cron.d/my_cron

CMD ["cron", "-f"]

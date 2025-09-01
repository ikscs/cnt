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
RUN chmod +x *.sh

COPY my_cron ./2.tmp
COPY .env ./1.tmp

RUN cat 1.tmp 2.tmp > /etc/cron.d/my_cron && \
    chmod 0644 /etc/cron.d/my_cron && \
    crontab /etc/cron.d/my_cron

RUN rm -rf *.tmp

EXPOSE 8000

CMD ["./entrypoint.sh"]

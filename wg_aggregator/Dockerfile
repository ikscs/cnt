FROM linuxserver/wireguard:latest

WORKDIR /app

RUN apk add --no-cache \
    python3 \
    py3-pip \
    curl \
    mc \
    libpq

RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    postgresql-dev \
    python3-dev \
    libffi-dev

COPY requirements.txt .
RUN python3 -m venv /lsiopy && \
    /lsiopy/bin/pip install --no-cache-dir -r requirements.txt

RUN apk del .build-deps
RUN rm -rf /var/cache/apk/*

COPY ./app /app
RUN chmod +x /app/*.*

ENV PATH="/lsiopy/bin:$PATH" \
    S6_KEEP_ENV=1

EXPOSE 8000 10001-20000

CMD ["tail", "-f", "/dev/null"]

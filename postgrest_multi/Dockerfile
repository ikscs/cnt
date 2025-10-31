FROM alpine:3.20

RUN apk add --no-cache bash curl gettext mc ca-certificates tar xz

ENV PGRST_VERSION=v13.0.7
RUN curl -L -o /tmp/postgrest.tar.xz \
      https://github.com/PostgREST/postgrest/releases/download/${PGRST_VERSION}/postgrest-${PGRST_VERSION}-linux-static-x86-64.tar.xz \
    && tar -xf /tmp/postgrest.tar.xz -C /usr/local/bin \
    && chmod +x /usr/local/bin/postgrest \
    && rm /tmp/postgrest.tar.xz

COPY api.template.conf /etc/postgrest/api.template.conf
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY healthcheck.sh /usr/local/bin/healthcheck.sh
COPY keys/. /etc/postgrest/

RUN chmod +x /usr/local/bin/entrypoint.sh /usr/local/bin/healthcheck.sh

EXPOSE 3000-3010

HEALTHCHECK --interval=60s --timeout=5s --retries=3 CMD /usr/local/bin/healthcheck.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

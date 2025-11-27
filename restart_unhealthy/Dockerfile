FROM alpine:3.20

RUN apk add --no-cache docker-cli bash

COPY restart-unhealthy.sh /restart-unhealthy.sh
RUN chmod +x /restart-unhealthy.sh

ENTRYPOINT ["/restart-unhealthy.sh"]

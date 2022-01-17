FROM alpine

RUN apk update \
  && apk upgrade \
  && apk add python3 docker-py py3-redis py3-dateutil \
  && rm -f /var/cache/apk/*

COPY swim_consumer_watchdog.py .

CMD ["python3", "swim_consumer_watchdog.py"]

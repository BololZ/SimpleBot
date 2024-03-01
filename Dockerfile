# syntax=docker/dockerfile:1

FROM python:alpine as builder

RUN apk --no-cache -U add libpq-dev build-base
WORKDIR /opt
COPY requirements.txt requirements.txt
RUN python -m venv /opt/venv && /opt/venv/bin/pip install -r requirements.txt --no-cache-dir

FROM python:alpine as main
RUN apk --no-cache -U add libpq && adduser -D -g "A Simple Discord Bot" -h /app simple
USER simple:simple
WORKDIR /app
COPY . .
COPY --from=builder --chmod=0550 /opt/venv /app/venv

ENTRYPOINT ["/app/venv/bin/python"]
CMD ["-u" , "./main.py"]

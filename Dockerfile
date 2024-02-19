# syntax=docker/dockerfile:1

FROM python:alpine

RUN apk --no-cache -U add libpq-dev build-base

RUN adduser -D -g "A Simple Discord Bot" simple

USER simple:simple

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

ENTRYPOINT ["python3"]
CMD ["-u" , "./main.py"]

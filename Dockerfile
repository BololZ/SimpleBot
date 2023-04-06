# syntax=docker/dockerfile:1

FROM python:alpine

RUN apk -U add py3-psycopg2 py3-aiohttp && apk cache clean

RUN adduser -D -g "A Simple Discord Bot" simple

USER simple:simple

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt --no-cache-dir && apk cache clean

COPY . .

ENTRYPOINT ["python3"]
CMD ["-u" , "./main.py"]

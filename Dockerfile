# syntax=docker/dockerfile:1

FROM python:alpine as builder

RUN apk --no-cache -U add libpq-dev build-base
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt --no-cache-dir

FROM python:alpine as main
RUN apk --no-cache -U add libpq && adduser -D -g "A Simple Discord Bot" simple
USER simple:simple
WORKDIR /app
COPY --from=builder /app/* /app/

ENTRYPOINT ["python3"]
CMD ["-u" , "./main.py"]

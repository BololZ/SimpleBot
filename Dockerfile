# syntax=docker/dockerfile:1

FROM python:alpine

RUN addgroup simple && adduser -D -g "A Simple Discord Bot" simple simple

USER simple:simple

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt --no-cache-dir --user

COPY . .

ENTRYPOINT ["python3"]
CMD ["-u" , "./main.py"]

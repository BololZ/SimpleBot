# syntax=docker/dockerfile:1

FROM python:latest

RUN groupadd simple && useradd --no-log-init -g simple simple

USER simple:simple

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT ["python3"]
CMD ["-u" , "./main.py"]
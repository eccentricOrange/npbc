FROM python:latest

RUN apt update
RUN apt install sqlite3 -y

ADD ./requirements.txt requirements.txt

RUN pip install -r requirements.txt pytest
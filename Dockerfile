FROM python:3.10.4

RUN apt-get update
RUN apt-get install sqlite3 -y

ADD ./requirements.txt requirements.txt

RUN pip install -r requirements.txt pytest


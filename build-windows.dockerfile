FROM --platform=windows/x86-64 python:3.10.4-windowsservercore

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt pyinstaller
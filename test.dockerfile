FROM python:3.10.4

RUN wget https://sqlite.org/2022/sqlite-autoconf-3380500.tar.gz
RUN tar -xvf sqlite-autoconf-3380500.tar.gz
WORKDIR sqlite-autoconf-3380500
RUN ./configure
RUN make
RUN make install
RUN export PATH="/usr/local/lib:$PATH"

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt pytest
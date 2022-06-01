FROM python:3.10.4

# build and install SQLite because >=3.35 is needed
RUN wget https://sqlite.org/2022/sqlite-autoconf-3380500.tar.gz
RUN tar -xvf sqlite-autoconf-3380500.tar.gz
WORKDIR sqlite-autoconf-3380500
RUN ./configure
RUN make
RUN make install
RUN export PATH="/usr/local/lib:$PATH"

# get python requirements
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt pytest

# create a new user who will actually run stuff
ARG USERNAME=dev
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME
FROM python:3.6-stretch

ENV FLASK_APP app.py
ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# install system stuff
COPY install.sh /usr/src/app
RUN sh install.sh

# install requirements
COPY requirements.txt /usr/src/app/
RUN pip install --disable-pip-version-check --no-cache-dir -r requirements.txt

COPY . /usr/src/app

CMD flask run -h 0.0.0.0 -p 8080

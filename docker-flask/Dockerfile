FROM ubuntu:20.04

RUN apt-get update -y
RUN apt-get install python3-pip -y
RUN apt-get install gunicorn -y
RUN apt-get install python3-setuptools -y
RUN apt-get install libmysqlclient-dev python3-dev -y
RUN apt-get install mysql-client -y

COPY requirements.txt requirements.txt
COPY flaskapp /opt/

RUN pip3 install --upgrade pip
RUN pip3 install setuptools-rust

RUN pip3 install -r requirements.txt

WORKDIR /opt/

CMD [ "gunicorn","-b", "0.0.0.0:8000", "app:app", "--workers=5", "--timeout=1000", "--log-level=debug"]




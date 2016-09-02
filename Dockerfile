FROM ubuntu:14.04.5

RUN apt-get -y update && apt-get install -y libmysqlclient-dev python \
python-dev python-pip

RUN pip install flask

RUN pip install flask-mysqldb

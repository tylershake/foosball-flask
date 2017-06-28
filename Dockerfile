FROM ubuntu:14.04.5

RUN apt-get -y update && apt-get install -y build-essential libmysqlclient-dev \
python python-dev python-pip

RUN pip install flask

RUN pip install trueskill

RUN pip install mysql-python

RUN pip install plotly

COPY . /app

WORKDIR /app

CMD python ./foosball-flask/foosball_flask.py

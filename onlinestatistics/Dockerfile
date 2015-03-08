FROM ubuntu:14.10
WORKDIR /code
ADD requirements.txt /code/
RUN  apt-get update&& \
	apt-get build-dep -y python-lxml&& \
	apt-get install -y \
	python-pip \
	libpq-dev python-dev&& \
    pip install -r requirements.txt
ADD . /code/
CMD python online.py

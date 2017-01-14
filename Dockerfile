FROM ubuntu

MAINTAINER Rod Glover <rglover@uvic.ca>

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get -yq install \
        libpq-dev \
        python3 \
        python3-dev \
        python3-pip \
        postgresql-client

ADD . /app
WORKDIR /app

RUN pip3 install -U pip
# RUN pip3 install psycopg2
RUN pip3 install -i https://pypi.pacificclimate.org/simple/ -r requirements.txt
RUN pip3 install .
# RUN python3 ./setup.py install

EXPOSE 8000

CMD devserver.py -p 8000 -t

FROM pcic/geospatial-python

ADD . /app
WORKDIR /app

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get -yq install postgresql postgresql-contrib postgis postgresql-9.3-postgis-2.1
RUN pip3 install -U pip
RUN pip3 install -i https://pypi.pacificclimate.org/simple/ -r requirements.txt
RUN python3 ./setup.py install
RUN ./sudo-user.sh

EXPOSE 8000

CMD devserver.py -p 8000 -t

#
# this is pretty hacky, just moving this older software over to a
# new dockerised machine. I'll clean up at some point :-)
#

# don't use the python container, as a bunch of our deps are a pain
# in the neck to compile, so we're better off using debian's system
# python
FROM debian:jessie
MAINTAINER Grahame Bowland <grahame@angrygoats.net>

ARG GIT_TAG=next
ARG PIP_OPTS="--no-cache-dir"

ENV GITTAG $GIT_TAG

# this is a bit of a kitchen sink. we use this container to
# run ealgis 'recipes'; at some point we should break the recipe
# container out
#
# postgis is only needed for the shp2pgsql binary
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3.4 \
      uwsgi-plugin-python3 \
      python3-pip \
      python3-psycopg2 \
      wget less git && \
  apt-get autoremove -y --purge && \
  apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app

RUN pip3 install -U "pip<8"

RUN pip3 ${PIP_OPTS} install \
    simplejson markdown flask flask-sqlalchemy && \
  rm -rf /root/.cache/pip/

COPY . /app

#RUN echo "building from git tag $GIT_TAG" && \
#    git clone --depth=1 --branch=$GITTAG https://github.com/grahame/hansardku.git .

RUN cd /app/code/ && pip3 install .

RUN adduser --system --uid 1000 --shell /bin/bash hansardku
USER hansardku
ENV HOME /app

EXPOSE 8889
VOLUME ["/app", "/data"]

COPY docker-entrypoint.sh /docker-entrypoint.sh

# entrypoint shell script that by default starts runserver
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uwsgi"]

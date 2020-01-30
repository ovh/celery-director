FROM python:3.8
ARG DIRECTOR_HOME
ENV DIRECTOR_HOME=${DIRECTOR_HOME:-/app/workflows/}
COPY director/ /app/director/
COPY setup.py /app/
COPY requirements.txt /app/
COPY entrypoint.sh /
WORKDIR /app
RUN python setup.py install
ENTRYPOINT ["/entrypoint.sh"]
CMD ["webserver"]
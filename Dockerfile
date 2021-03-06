FROM python:3.8.6-slim-buster

WORKDIR /root/flask-app
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends less procps

EXPOSE 5000
CMD /bin/bash

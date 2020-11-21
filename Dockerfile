FROM python:3.8.6-slim-buster

WORKDIR /root
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

CMD /bin/bash

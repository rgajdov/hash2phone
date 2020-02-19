FROM python:3.6-alpine

RUN adduser -D phonedb

WORKDIR /home/phonedb

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY phonedb.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP phonedb.py

RUN chown -R phonedb:phonedb ./
USER phonedb

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]

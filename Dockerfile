FROM python:3.6

WORKDIR /app
EXPOSE 5000
VOLUME /data

COPY . .

RUN python setup.py install

ENV FLASK_APP=lunchbot
ENV LUNCHBOT_SETTINGS=/data/lunchbot.cfg

CMD flask run --host=0.0.0.0

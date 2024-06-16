FROM python:3.11

ENV PYTHONUNBUFFERED=1

WORKDIR /app

ADD . .

RUN mkdir /app/input

VOLUME /app/input

ENV PYTHONPATH="${PYTHONPATH}:/app"

ENTRYPOINT ["python", "src/main.py"]

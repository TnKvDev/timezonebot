# Dockerfile, Image, Container
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ADD timezoneBot.py /app
ADD database.py /app
COPY cogs/ /app/cogs/
ADD requ.txt /app

RUN pip install -r requ.txt

CMD ["python3", "./timezoneBot.py"]

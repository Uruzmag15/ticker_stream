FROM python:3.7

#Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
COPY . /code/
RUN pip install -r requirements.txt

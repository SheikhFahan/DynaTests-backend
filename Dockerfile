FROM python:3.11-slim-buster
ENV PYTHONUNBUFFERED=1
WORKDIR  /dynatest_backend
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

  


FROM apache/spark-py:latest

USER root

WORKDIR /app

RUN apt-get update -y &&\
    apt-get install -y python3 &&\
    pip3 install pyspark==3.3.0

COPY my_etl.py .
COPY ./raw ./raw

CMD ["python3", "my_etl.py"]

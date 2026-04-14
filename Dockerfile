FROM apache/airflow:2.9.3

USER root
RUN apt-get update && apt-get install -y build-essential && apt-get clean

USER airflow
RUN pip install --no-cache-dir \
    pandas \
    numpy \
    tensorflow \
    Pillow \
    psycopg2-binary \
    dbt-postgres \
    python-dotenv

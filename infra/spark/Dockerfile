FROM apache/spark:3.5.1

ARG ICEBERG_VERSION=1.5.2
ARG ICEBERG_RUNTIME_JAR=iceberg-spark-runtime-3.5_2.12-${ICEBERG_VERSION}.jar

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    python3 \
    && curl -fL "https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/${ICEBERG_VERSION}/${ICEBERG_RUNTIME_JAR}" \
      -o "/opt/spark/jars/${ICEBERG_RUNTIME_JAR}" \
    && ln -sf /usr/bin/python3 /usr/local/bin/python \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

USER spark

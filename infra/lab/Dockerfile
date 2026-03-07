FROM apache/spark:3.5.1

ARG ICEBERG_VERSION=1.5.2
ARG ICEBERG_RUNTIME_JAR=iceberg-spark-runtime-3.5_2.12-${ICEBERG_VERSION}.jar

USER root

COPY infra/lab/pyspark_novalake_kernel.json /tmp/pyspark_novalake_kernel.json

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl -fL "https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/${ICEBERG_VERSION}/${ICEBERG_RUNTIME_JAR}" \
      -o "/opt/spark/jars/${ICEBERG_RUNTIME_JAR}" \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir \
    pyspark==3.5.1 \
    jupyterlab==4.2.5 \
    ipykernel==6.29.5 \
    pandas==2.0.3 \
    matplotlib==3.7.5 \
    && mkdir -p /home/spark/.local/share/jupyter/runtime \
    && mkdir -p /home/spark/.local/share/jupyter/kernels/pyspark-novalake \
    && mkdir -p /home/spark/.jupyter \
    && cp /tmp/pyspark_novalake_kernel.json /home/spark/.local/share/jupyter/kernels/pyspark-novalake/kernel.json \
    && chown -R spark:root /home/spark

USER spark
WORKDIR /opt/novalake/notebooks
ENV HOME=/home/spark

ENTRYPOINT ["/bin/bash", "-lc"]
CMD ["jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --ServerApp.token='' --ServerApp.password='' --ServerApp.root_dir=/opt/novalake/notebooks"]

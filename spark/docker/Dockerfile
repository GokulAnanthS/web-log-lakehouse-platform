FROM apache/spark:3.5.0

USER root

# Install Python and pip (needed for delta-spark)
RUN apt-get update && apt-get install -y python3 python3-pip curl

# Install Delta Lake
RUN pip3 install delta-spark

# Set environment variables
ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH

WORKDIR /app

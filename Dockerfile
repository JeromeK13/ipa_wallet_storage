# Build stage container
FROM ubuntu:bionic

# Set runtime configurations
WORKDIR /usr/app
ENV PYTHONPATH .

# Install python
RUN apt-get -yqq update -yqq && apt-get -yqq install \
    software-properties-common \
    apt-transport-https \
    python3.7-dev \
    python3.7 \
    python3-pip \
    git

# Install libindy
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 68DB5E88 && \
    add-apt-repository "deb https://repo.sovrin.org/sdk/deb xenial stable" && \
    apt-get -yqq update && \
    apt-get -yqq install libindy=1.14.2

# Install Python packages
COPY requirements.txt ./requirements.txt
RUN python3.7 -m pip install -r ./requirements.txt

# Copy src
COPY src ./src
# Create Log folder
RUN mkdir logs
# Expose app port
EXPOSE 8080
# Start app
CMD ["uvicorn","src.main:app", "--host", "0.0.0.0", "--port", "8080"]




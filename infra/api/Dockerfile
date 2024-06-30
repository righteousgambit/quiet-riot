# Use an official Ubuntu image as the base
FROM ubuntu:22.04

WORKDIR /code

# Set environment variables to non-interactive (this ensures that no prompts are displayed during package installation)
ENV DEBIAN_FRONTEND=noninteractive

# Preconfigure tzdata package
RUN echo "tzdata tzdata/Areas select Etc" | debconf-set-selections && \
    echo "tzdata tzdata/Zones/Etc select UTC" | debconf-set-selections

# Add the deadsnakes PPA, update, and install dependencies
RUN apt-get update && apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa -y && \
    apt-get update && apt-get install -y \
    libblas-dev \
    liblapack-dev \
    gfortran \
    gcc \
    g++ \
    build-essential \
    libgdal-dev \
    libcairo2-dev \
    libopenblas-dev \
    libdbus-1-dev \
    libgirepository1.0-dev \
    python3.11 \
    python3.11-distutils \
    python3.11-dev \
    python3-pip \
    graphviz \
    libgraphviz-dev \
    portaudio19-dev \
    cmake \
    curl \
    git \
    gnupg

# Upgrade pip
RUN python3.11 -m pip install --upgrade pip

# Optionally make Python 3.9 as the default python3 version
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

RUN apt install --upgrade awscli -y

# Copy the requirements file
COPY ./requirements.txt /code/requirements.txt

# Install Python packages and ignore installed packages
RUN pip3 install --no-cache-dir --upgrade -r /code/requirements.txt --ignore-installed

# Copy the app
COPY ./app /code/app

# # Command to run when the container starts
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "443"]
FROM ubuntu:latest 

MAINTAINER AIR Institute "dabm@air-institute.org"

WORKDIR /app

# tzdata
ENV TZ=Europe/Madrid
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Main apt stuff
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python-dev \
    python3-dev \
    python3-pip \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    ca-certificates \
    build-essential \
    git \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# clone smartclide-smart-assistant
RUN git clone https://github.com/eclipse-researchlabs/smartclide-service-discovery-poc.git

# build ServiceDiscovery
RUN cd smartclide-service-discovery-poc/ServiceDiscovery && \
    python3 -m pip install --no-cache-dir -r requirements.txt && \
    python3 -m pip install . --upgrade

EXPOSE 2020
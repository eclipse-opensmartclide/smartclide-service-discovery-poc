#*******************************************************************************
# Copyright (C) 2022 AIR Institute
# 
# This program and the accompanying materials are made
# available under the terms of the Eclipse Public License 2.0
# which is available at https://www.eclipse.org/legal/epl-2.0/
# 
# SPDX-License-Identifier: EPL-2.0
# 
# Contributors:
#    David Berrocal Macías (@dabm-git) - initial API and implementation
#*******************************************************************************

# Download the base image ubuntu v20.04
FROM ubuntu:20.04

MAINTAINER AIR Institute "dberrocal@air-institute.com"

WORKDIR /app

# tzdata
ENV TZ=Europe/Madrid
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Main apt stuff
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-dev \
    python3-pip \
    python3-tk \
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
RUN git clone https://github.com/eclipse-opensmartclide/smartclide-service-discovery-poc.git

# build ServiceDiscovery
RUN cd smartclide-service-discovery-poc/ServiceDiscovery && \
    python3 -m pip install --no-cache-dir -r requirements.txt && \
    python3 -m pip install . --upgrade

EXPOSE 2020

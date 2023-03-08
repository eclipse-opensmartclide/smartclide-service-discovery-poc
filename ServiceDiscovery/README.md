<!--
   Copyright (C) 2021-2022 AIR Institute
   
   This program and the accompanying materials are made
   available under the terms of the Eclipse Public License 2.0
   which is available at https://www.eclipse.org/legal/epl-2.0/
   
   SPDX-License-Identifier: EPL-2.0
   
   Contributors:
       David Berrocal Macías (@dabm-git) - initial API and implementation
-->
# Service Discovery API - SmartCLIDE
Maintainer:  @dabm-git - AIR Institute

## Configure 
This package relies on tokens from GitGub, GitLab and BitBucket APIs that are configured in the config.ini file in the root of the service.
The service also relies on a database instance to store information, and in the classification service offered by SmartCLIDE's DLE component to classify the discovered services, where the configuration of the IP, port and credentials are done in this same file.
    See: https://github.com/eclipse-opensmartclide/smartclide-service-discovery-poc/blob/main/ServiceDiscovery/config.ini

The service makes use of the 2020 port, be sure to expose it.

## Build
```
    python3 -m pip install --no-cache-dir -r requirements.txt
    python3 -m pip install . --upgrade
```
Or build the image with the provided dockerfile.

## Run
```
python3 servicediscovery
```

Or using the built docker image hosted by ghcr.io, with docker-compose.
```
docker-compose up
```

```
version: '3'

services:
  service_discovery:
    restart: unless-stopped
    image: ghcr.io/eclipse-opensmartclide/smartclide/service-discovery:2022-04-04
    working_dir: /app/smartclide-service-discovery-poc/ServiceDiscovery
    command: python3 ServiceDiscovery
    ports:
      - "2020:2020"
```

Be sure to replace the necessary configuration in the [config.ini](https://github.com/eclipse-opensmartclide/smartclide-service-discovery-poc/blob/main/ServiceDiscovery/config.ini) file, to do this you can overwrite it with the following section in docker-compose.yml:
```
volumes:
 -./config.ini:/app/smartclide-service-discovery-poc/ServiceDiscovery/config.ini
```


# Web service listings - SmartCLIDE
Maintainer:  @dabm-git - AIR Institute

## Run
This script collects information from Programableweb, to avoid saturation and blocking of IP addresses by a high number of requests, this script can be executed on a regular basis, obtaining a section each time.

When launched, information is collected in batches that are exported to .csv files, and when a batch is finished, the results are merged under the same .csv file.

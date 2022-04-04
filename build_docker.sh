#!/bin/bash
# Eclipse Public License 2.0

docker build --tag ghcr.io/eclipse-researchlabs/smartclide/service-discovery:$(date +'%Y-%m-%d') .
docker push ghcr.io/eclipse-researchlabs/smartclide/service-discovery:$(date +'%Y-%m-%d')
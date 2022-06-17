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

docker build --tag ghcr.io/eclipse-researchlabs/smartclide/service-discovery:$(date +'%Y-%m-%d') .
docker push ghcr.io/eclipse-researchlabs/smartclide/service-discovery:$(date +'%Y-%m-%d')
#docker build --tag ghcr.io/eclipse-researchlabs/smartclide/service-discovery:latest .
#docker push ghcr.io/eclipse-researchlabs/smartclide/service-discovery:latest
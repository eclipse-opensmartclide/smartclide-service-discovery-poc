<!--
   Copyright (C) 2021-2022 AIR Institute
   
   This program and the accompanying materials are made
   available under the terms of the Eclipse Public License 2.0
   which is available at https://www.eclipse.org/legal/epl-2.0/
   
   SPDX-License-Identifier: EPL-2.0
   
   Contributors:
       David Berrocal Macías (@dabm-git) - initial API and implementation
-->
# Web service listings - SmartCLIDE
Maintainer:  @dabm-git - AIR Institute

## Run
This script collects information from Programableweb, to avoid saturation and blocking of IP addresses by a high number of requests, this script can be executed on a regular basis, obtaining a section each time.

When launched, information is collected in batches that are exported to .csv files, and when a batch is finished, the results are merged under the same .csv file.

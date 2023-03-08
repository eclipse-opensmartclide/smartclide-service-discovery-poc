# *******************************************************************************
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
# *******************************************************************************

from utils import ConfigReader


class FlaskConfig():
    # API config
    PORT = 2020
    HOST = '0.0.0.0'
    URL_PREFIX = '/servicediscovery/v1'
    # NOTE: namesapce is not available in debug mode, you must specify the namespace servicediscovery
    DEBUG_MODE = False
    USE_HTTPS = False
    SSL_KEY = './certs/server.key'
    SSL_CERT = './certs/server.crt'


class ServiceDiscoeryConfig():
    # GitHub API
    GITHUB_ACCESS_TOKEN_1 = ConfigReader.read_config(section='tokens')[
        'github_token']
    # GitLab API
    GITLAB_ACCESS_TOKEN_1 = ConfigReader.read_config(section='tokens')[
        'gitlab_token']
    # BitBucket API - not used, web crawler is used

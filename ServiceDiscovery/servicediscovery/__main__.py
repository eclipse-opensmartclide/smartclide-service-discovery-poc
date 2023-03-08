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

from flask import Flask, Blueprint, redirect, request
from flask_cors import CORS
from flask_talisman import Talisman
import ssl
import logging

# own
from config import FlaskConfig
from api.api import api
from core import cache, limiter
from utils import PrintLog

# namespaces
from api.github_api import github_ns
from api.gitlab_api import gitlab_ns
from api.bitbucket_api import bitbucket_ns

app = Flask(__name__)

VERSION = (1, 0)
AUTHOR = 'David Berrocal Macías - AIR Institute (dberrocal@air-institute.com)'

namespaces = [github_ns, gitlab_ns, bitbucket_ns]


def get_version():
    """
    This function returns the API version that is being used.
    """
    return '.'.join(map(str, VERSION))


def get_authors():
    """
    This function returns the API's author name.
    """
    return str(AUTHOR)


__version__ = get_version()
__author__ = get_authors()


@app.route('/')
def register_redirection():
    """
    Redirects to dcoumentation page.
    """
    return redirect(f'{request.url_root}/{FlaskConfig.URL_PREFIX}', code=302)


def initialize_app(flask_app):
    """
    This function initializes the Flask Application, adds the namespace and registers the blueprint.
    """
    CORS(flask_app)

    v1 = Blueprint('api', __name__, url_prefix=FlaskConfig.URL_PREFIX)
    api.init_app(v1)

    limiter.exempt(v1)
    cache.init_app(flask_app)

    flask_app.register_blueprint(v1)
    flask_app.config.from_object(FlaskConfig)

    for ns in namespaces:
        api.add_namespace(ns)


def main():
    # logging
    logging.basicConfig(handlers=[logging.FileHandler(filename='servicediscovery_api.log',
                                                      encoding='utf-8')],
                        level=logging.INFO,
                        format='%(asctime)s %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p')

    initialize_app(app)

    separator_str = ''.join(map(str, ["=" for _ in range(175)]))

    PrintLog.log(separator_str)
    PrintLog.log(f'Debug mode: {FlaskConfig.DEBUG_MODE}')
    PrintLog.log(f'HTTPS: {FlaskConfig.USE_HTTPS}')

    if FlaskConfig.USE_HTTPS:
        PrintLog.log(f'\tcert: {FlaskConfig.SSL_CERT}')
        PrintLog.log(f'\tkey: {FlaskConfig.SSL_KEY}')

    PrintLog.log(f'Authors: {get_authors()}')
    PrintLog.log(f'Version: {get_version()}')
    PrintLog.log(
        f'Base URL: http://localhost:{FlaskConfig.PORT}{FlaskConfig.URL_PREFIX}')
    PrintLog.log(separator_str)

    if not FlaskConfig.USE_HTTPS:
        app.run(host=FlaskConfig.HOST, port=FlaskConfig.PORT,
                debug=FlaskConfig.DEBUG_MODE, threaded=True)
    else:
        Talisman(app, force_https=True)
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(FlaskConfig.SSL_CERT, FlaskConfig.SSL_KEY)
        app.run(host=FlaskConfig.HOST, port=FlaskConfig.PORT,
                debug=FlaskConfig.DEBUG_MODE, threaded=True, ssl_context=context)


if __name__ == '__main__':
    main()

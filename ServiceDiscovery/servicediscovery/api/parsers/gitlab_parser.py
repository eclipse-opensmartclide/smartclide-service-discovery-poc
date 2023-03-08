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

from flask_restx import reqparse

gitlab_argument_parser = reqparse.RequestParser()

gitlab_argument_parser.add_argument('from_url',
                                    location='args',
                                    type=str,
                                    required=False,
                                    default=None,
                                    help='The GitLab URL user/org to retrieve repo information from.')

gitlab_argument_parser.add_argument('from_keyword',
                                    location='args',
                                    type=str,
                                    required=False,
                                    default=None,
                                    help='The keyword to retrieve repos information from.')

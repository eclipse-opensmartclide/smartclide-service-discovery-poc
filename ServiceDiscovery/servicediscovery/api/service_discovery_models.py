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

from flask_restx import fields
from api.api import api

service_insert_model = api.model('Insert Service Request', {
    'full_name': fields.String(description="The name of the service to insert", required=True, example="TransLoc openAPI"),
    'link': fields.String(description="The link of the service to insert", required=True, example="https://transloc-api.com/docs/"),
    'stars': fields.Integer(description="The number of stars of the service to insert", required=True, example=0),
    'forks':    fields.Integer(description="The number of forks of the service to insert", required=True, example=0),
    'watchers' :  fields.Integer(description="The number of watchers of the service to insert", required=True, example=0),
    'updated_on' : fields.String(description="The date of the last update of the service to insert", required=True, example="2020-01-01"),
    'keywords' : fields.String(description="The keywords of the service to insert", required=True, example="transloc, openapi"),
    'source' : fields.String(description="The source of the service to insert", required=True, example="user_dabm"),
    'uuid' : fields.String(description="The uuid of the service to insert", required=True, example="123456789"),    
}, description="Information of the service to insert in the database.")


service_insert_model_example = api.model('Search Insert Response', {
    'status': fields.String(description="Data inserted correctly", required=True, example="Data inserted correctly"),
}, description="Status of the service inserted in the database.")


service_search_model = api.model('Search Service Request', {
    'full_name': fields.String(description="The name of the service to search", required=True, example="TransLoc openAPI"),
    'keywords' : fields.String(description="The keywords of the service to search", required=True, example="transloc, openapi"),
    'description' : fields.String(description="The description of the service to search", required=True, example="TransLoc openAPI description"),
    }, description="Information of the service to search in the database.")

service_search_model_example = api.model('Search Service Response', {
    'full_name': fields.String(description="The name of the service found", required=True, example="TransLoc openAPI"),
    'link': fields.String(description="The link of the service found", required=True, example="https://transloc-api.com/docs/"),
    'stars': fields.Integer(description="The number of stars of the service found", required=True, example=0),
    'forks':    fields.Integer(description="The number of forks of the service found", required=True, example=0),
    'watchers' :  fields.Integer(description="The number of watchers of the service found", required=True, example=0),
    'updated_on' : fields.String(description="The date of the last update of the service found", required=True, example="2020-01-01"),
    'keywords' : fields.String(description="The keywords of the service found", required=True, example="transloc, openapi"),
    'source' : fields.String(description="The source of the service to found", required=True, example="user_dabm"),
    'uuid' : fields.String(description="The uuid of the service found", required=True, example="123456789"),    
}, description="List of services found in the database.")


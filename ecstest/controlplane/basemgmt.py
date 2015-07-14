# __CR__
# Copyright (c) 2008-2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.
# __CR__

'''
Author: Rubicon ISE team
'''

from ecstest import constants, config, client

cfg = config.get_config()

class BaseMgmt(object):
    '''
    Base management class
    '''
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.client = client.EcsControlPlaneClient(username=username,
                                                   password=password,
                                                   token=cfg['TOKEN'],
                                                   ecs_endpoint=cfg['CONTROL_ENDPOINT'],
                                                   token_endpoint=cfg['TOKEN_ENDPOINT'],
                                                   verify_ssl=cfg['VERIFY_SSL'],
                                                   token_filename=cfg['TOKEN_FILENAME'],
                                                   request_timeout=cfg['REQUEST_TIMEOUT'],
                                                   cache_token=cfg['CACHE_TOKEN']
                                                  )

    def login(self, accept_header=constants.APPLICATION_JSON):
        '''
        Request a new authentication token from ECS.
        '''
        token = self.client.token
        if not token:
            response = self.client.make_login_request(self.username, self.password, accept_header)
            if response.status_code == 200:
                token = response.headers.get('X-SDS-AUTH-TOKEN', None)
            else:
                response.raise_for_status()
        return token

    def logout(self, accept_header=constants.APPLICATION_JSON,
               content_type=constants.APPLICATION_JSON):
        '''
        End http session.
        '''
        return self.client.make_logout_request(self.client.token, accept_header, content_type)


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

from ecstest import constants, config
from ecstest.controlplane.basemgmt import BaseMgmt

cfg = config.get_config()

class UserAdmin(BaseMgmt):
    '''
    User admin and do some management operations
    '''
    def __init__(self):
        super(UserAdmin, self).__init__(cfg['ADMIN_USERNAME'], cfg['ADMIN_PASSWORD'])

    def create_user(self, user, namespace=cfg['NAMESPACE'], tags=None,
                    accept_header=constants.APPLICATION_JSON,
                    content_type=constants.APPLICATION_JSON):
        '''
        Create user by admin
        '''
        #check admin login firstly
        self.login()

        user_info = {}
        response = self.client.user_management.create_object_user(user, namespace,
                                                                  tags=tags,
                                                                  accept_header=accept_header,
                                                                  content_type=content_type
                                                                 )
        if response.status_code == 200:
            user_info = self.get_user_info(user, namespace)
        else:
            response.raise_for_status()

        return user_info

    def delete_user(self, user, namespace=cfg['NAMESPACE'],
                    accept_header=constants.APPLICATION_JSON,
                    content_type=constants.APPLICATION_JSON):
        '''
        Delete user by admin
        '''
        #check admin login firstly
        self.login()
        return self.client.user_management.deactivate_object_user(user, namespace,
                                                                  accept_header=accept_header,
                                                                  content_type=content_type
                                                                 )

    def get_user_info(self, user, namespace=cfg['NAMESPACE'],
                      accept_header=constants.APPLICATION_JSON,
                      content_type=constants.APPLICATION_JSON):
        '''
        Get user info by admin
        '''
        #check admin login firstly
        self.login()

        user_info = {}
        response = self.client.user_management.get_object_user_info(user, namespace=namespace,
                                                                    accept_header=accept_header,
                                                                    content_type=content_type
                                                                   )
        if response.status_code == 200:
            user_info = response.json()
        else:
            response.raise_for_status()
        return user_info

    def create_secret_key(self, user, secret_key=None, namespace=cfg['NAMESPACE'],
                          accept_header=constants.APPLICATION_JSON,
                          content_type=constants.APPLICATION_JSON):
        '''
        Create secret key for user by admin
        '''
        #check admin login firstly
        self.login()

        if not self.get_user_info(user, namespace):
            self.create_user(user, namespace)

        response = self.client.secret_key_management.create_secret_key(user, secret_key,
                                                                       namespace=namespace,
                                                                       accept_header=accept_header,
                                                                       content_type=content_type
                                                                      )
        if response.status_code == 200:
            secret_key = response.json()['secret_key']
        else:
            response.raise_for_status()
        return secret_key

    def get_secret_keys(self, user,
                        accept_header=constants.APPLICATION_JSON,
                        content_type=constants.APPLICATION_JSON):
        """
        Get all secret keys for an user
        """

        #check admin login firstly
        self.login()

        secret_keys = []

        response = self.client.secret_key_management.get_secret_keys(user,
                                                                     accept_header,
                                                                     content_type
                                                                    )
        if response.status_code == 200:
            response_json = response.json()
            secret_keys = [value for key, value in response_json.items() if key.startswith('secret_key_')]
        else:
            response.raise_for_status()
        return secret_keys

    def delete_secret_key(self, user, secret_key=None, namespace=cfg['NAMESPACE'],
                          accept_header=constants.APPLICATION_JSON,
                          content_type=constants.APPLICATION_JSON):
        '''
        Delete a secret key for an user. If no key is supplied to
        this method, then the system will delete all secret keys.
        '''

        #check admin login firstly
        self.login()
        return self.client.secret_key_management.deactivate_secret_key(user, secret_key, namespace,
                                                                       accept_header=accept_header,
                                                                       content_type=content_type
                                                                      )

class UserCommon(BaseMgmt):
    '''
    Behavior related with common user
    '''
    def __init__(self, username, password):
        super(UserCommon, self).__init__(username, password)


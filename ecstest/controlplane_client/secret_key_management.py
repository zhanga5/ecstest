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


"""Test client class for interacting with the EMC ECS control plane - Object
User Secret Key resources.
"""

import json

from ecstest import constants


class SecretKeyManagement():

    def __init__(self, client):
        """
        Initialize a new instance
        """

        self.client = client

    def get_secret_keys(self, user,
                        accept_header=constants.APPLICATION_JSON,
                        content_type=constants.APPLICATION_JSON):
        """
        Get all secret keys for an object user
        """

        response = self.client.session.get(
            "{0}/object/user-secret-keys/{1}".format(
                self.client.ecs_endpoint,
                user
            ),
            verify=self.client.verify_ssl,
            headers=self.client._base_request_headers(accept_header, content_type),
            timeout=self.client.request_timeout
        )

        return response

    def create_secret_key(self, user, secret_key=None, existing_key_ttl=None,
                          namespace=None,
                          accept_header=constants.APPLICATION_JSON,
                          content_type=constants.APPLICATION_JSON):
        """
        Create a secret key for an object user. If no key is supplied to this
        method, the system will generate a random secret key.
        """

        payload = {}

        # Add in optionals.
        if secret_key:
            payload['secretkey'] = secret_key

        if existing_key_ttl:
            payload['existing_key_expiry_time_mins'] = existing_key_ttl

        if namespace:
            payload['namespace'] = namespace

        response = self.client.session.post(
            "{0}/object/user-secret-keys/{1}".format(
                self.client.ecs_endpoint,
                user
            ),
            verify=self.client.verify_ssl,
            data=json.dumps(payload),
            headers=self.client._base_request_headers(accept_header, content_type),
            timeout=self.client.request_timeout
        )

        return response

    def deactivate_secret_key(self, user, secret_key=None, namespace=None,
                              accept_header=constants.APPLICATION_JSON,
                              content_type=constants.APPLICATION_JSON):
        """
        Decativate a secret key for an object user. If no key is supplied to
        this method, then the system will delete all secret keys.
        """

        payload = {}

        # Add in optionals.
        if secret_key:
            payload['secret_key'] = secret_key

        if namespace:
            payload['namespace'] = namespace

        response = self.client.session.post(
            "{0}/object/user-secret-keys/{1}/deactivate".format(
                self.client.ecs_endpoint,
                user
            ),
            verify=self.client.verify_ssl,
            data=json.dumps(payload),
            headers=self.client._base_request_headers(accept_header, content_type),
            timeout=self.client.request_timeout
        )

        return response

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


"""Test client classes for interacting with the EMC ECS control/data planes.

Test clients allow the creation of both valid and invalid requests and return
low level response objects for use in TestCase assertions.
"""

import requests

from ecstest import constants
from ecstest.controlplane_client.user_management import UserManagement
from ecstest.controlplane_client.secret_key_management import SecretKeyManagement

# Disable InsecureRequestWarning for unverified HTTPS requests.
requests.packages.urllib3.disable_warnings()


ERROR_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "id": "http://jsonschema.net",
    "type": "object",
    "properties": {
        "retryable": {
            "type": "boolean"
        },
        "code": {
            "type": "integer"
        },
        "description": {
            "type": "string"
        },
    },
    "required": [
        "retryable", "code", "description"
    ]
}


class EcsControlPlaneClient(object):

    def __init__(self, username=None, password=None, token=None,
                 ecs_endpoint=None, token_endpoint=None, verify_ssl=False,
                 token_filename='/tmp/ecstest.token',
                 request_timeout=15.0, cache_token=True):
        """
        Creates an instance of client class used for interacting
        with the ECS control plane.

        :param username: The username to fetch a token
        :param password: The password to fetch a token
        :param token: Supply a valid token to use instead of username/password
        :param ecs_endpoint: The URL where ECS is located
        :param token_endpoint: The URL where the ECS login is located
        :param verify_ssl: Verify SSL certificates
        :param token_filename: The name of the cached token filename
        :param request_timeout: How long to wait for ECS to respond
        :param cache_token: Whether to cache the token, by default this is true
        you should only switch this to false when you want to directly fetch
        a token for a user
        """

        self.username = username
        self.password = password
        self.token = token
        self.ecs_endpoint = ecs_endpoint.rstrip('/')
        self.token_endpoint = token_endpoint.rstrip('/')
        self.verify_ssl = verify_ssl
        self.token_filename = token_filename
        self.request_timeout = request_timeout
        self.cache_token = cache_token
        self.session = requests.Session()
        self.token = None

        # Create client classes as attributes.
        self.user_management = UserManagement(self)
        self.secret_key_management = SecretKeyManagement(self)

    def make_login_request(self, username=None, password=None,
                           accept_header=constants.APPLICATION_JSON):
        """
        Request a new authentication token from ECS
        """
        if username is None:
            username = self.username
        if password is None:
            password = self.password

        self.session.auth = (username, password)

        response = self.session.get(
            self.token_endpoint,
            verify=self.verify_ssl,
            headers={'Accept': accept_header},
            timeout=self.request_timeout
        )

        # If successful, store auth token if requested.
        if response.status_code == 200:
            self.token = response.headers.get('X-SDS-AUTH-TOKEN')

            if self.cache_token:
                with open(self.token_filename, 'wb') as token_file:
                    token_file.write(self.token)

        return response

    def make_logout_request(self, token=None,
                            accept_header=constants.APPLICATION_JSON,
                            content_type=constants.APPLICATION_JSON):
        """
        End given control plane session
        """

        if not token:
            token = self.token

        response = self.session.get(
            "{0}/logout".format(self.ecs_endpoint),
            verify=self.verify_ssl,
            headers=self._base_request_headers(accept_header, content_type),
            timeout=self.request_timeout
        )

        # Clear auth token.
        if response.status_code == 200:
            self.token = None

        return response

    def _base_request_headers(self, accept_header, content_type):
        headers = {
            'Accept': accept_header,
            'Content-Type': content_type,
            'X-SDS-AUTH-TOKEN': self.token
        }

        return headers


class EcsDataPlaneClient():
    def __init__(self):
        pass

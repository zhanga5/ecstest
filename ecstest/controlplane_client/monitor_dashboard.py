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


"""Test client class for interacting with the EMC ECS control plane - User
Management resources.
"""

import json

from ecstest import constants


class UserManagement():

    def __init__(self, client):
        """
        Initialize a new instance
        """

        self.client = client

    def create_object_user(self, user, namespace, tags=None,
                           accept_header=constants.APPLICATION_JSON,
                           content_type=constants.APPLICATION_JSON):
        """
        Create a new object user
        """

        response = self.client.session.post(
            "{0}/object/users".format(self.client.ecs_endpoint),
            verify=self.client.verify_ssl,
            data=json.dumps(
                {
                    'user': user,
                    'namespace': namespace,
                    'tags': tags
                }
            ),
            headers=self.client._base_request_headers(accept_header, content_type),
            timeout=self.client.request_timeout
        )

        return response

    def deactivate_object_user(self, user, namespace,
                               accept_header=constants.APPLICATION_JSON,
                               content_type=constants.APPLICATION_JSON):
        """
        Deactivate an existing object user
        """

        response = self.client.session.post(
            "{0}/object/users/deactivate".format(self.client.ecs_endpoint),
            verify=self.client.verify_ssl,
            data=json.dumps(
                {
                    'user': user,
                    'namespace': namespace
                }
            ),
            headers=self.client._base_request_headers(accept_header, content_type),
            timeout=self.client.request_timeout
        )

        return response

    def get_object_user_info(self, user, namespace=None,
                             accept_header=constants.APPLICATION_JSON,
                             content_type=constants.APPLICATION_JSON):
        """
        Get info about an existing object user
        """

        url = "{0}/object/users/{1}/info".format(self.client.ecs_endpoint, user)

        if namespace:
            url += "?namespace={0}".format(namespace)

        response = self.client.session.get(
            url,
            verify=self.client.verify_ssl,
            headers=self.client._base_request_headers(accept_header, content_type),
            timeout=self.client.request_timeout
        )

        return response

    def set_lock_object_user(self, user, islocked, namespace=None,
                             accept_header=constants.APPLICATION_JSON,
                             content_type=constants.APPLICATION_JSON):
        """
        Lock/Unlock an object user
        """

        response = self.client.session.put(
            "{0}/object/users/lock".format(self.client.ecs_endpoint),
            verify=self.client.verify_ssl,
            data=json.dumps(
                {
                    'user': user,
                    'namespace': namespace,
                    'isLocked': islocked,
                }
            ),
            headers=self.client._base_request_headers(accept_header, content_type),
            timeout=self.client.request_timeout
        )

        return response

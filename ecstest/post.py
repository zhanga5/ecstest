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

import base64
import json
import time

from boto import utils

from ecstest import s3requests
from ecstest.utils import get_signature


def post_from_string(bucket, key_name, content, user_metadata=None):
    '''
    Set contents of key by POST method from string.
    '''
    return _post(bucket,
                 key_name,
                 content=content,
                 user_metadata=user_metadata)


def post_from_filename(bucket, key_name, pathfn, user_metadata=None):
    '''
    Set contents of key by POST method from filepath.
    '''
    return _post(bucket,
                 key_name,
                 pathfn=pathfn,
                 user_metadata=user_metadata)


def _post(bucket, key_name, pathfn=None, content=None, user_metadata=None):
    '''
    Support post with file or text together with user metadata
    '''
    # The policy document contains the expiration and conditions.
    # The expiration element specifies the expiration date of
    # the policy in ISO 8601 UTC date format.
    # Expiration is required in a policy.
    # The conditions in the policy document validate
    # the contents of the uploaded object.
    # Each form field that you specify in the form
    # (except AWSAccessKeyId, signature, file, policy,
    # and field names that have an x-ignore- prefix)
    # must be included in the list of conditions.
    expiration_time = time.gmtime(time.time() + 3600)
    policy = {
        "expiration": time.strftime(utils.ISO8601, expiration_time),
        "conditions": [
            {"bucket": bucket.name},
            {"key": key_name},
            {"acl": "public-read"},
            ["starts-with", "$Content-Type", "application/"],
        ]
    }

    # Any user metadata should be at policy
    if user_metadata is not None:
        for k, v in user_metadata.items():
            policy['conditions'].append({k: v})

    # Encode the policy by using UTF-8 of json dumps default encoding
    policy_encoded = base64.b64encode(json.dumps(policy))
    signature = get_signature(bucket.connection.provider.secret_key,
                              policy_encoded)

    # Order is retained if form_fields is a list of 2-tuples
    # but arbitrary if it is supplied as a dict.
    form_fields = [
        ('key', key_name),
        ('acl', 'public-read'),
        ('Content-Type', 'application/octet-stream'),
        ('AWSAccessKeyId', bucket.connection.provider.access_key),
        ('Policy', policy_encoded),
        ('Signature', signature),
    ]

    # Any user metadata should be as one form field
    if user_metadata is not None:
        for k, v in user_metadata.items():
            form_fields.append((k, v))

    files = {}
    if pathfn is not None:
        # This is to post a file.
        files = {'file': open(pathfn, 'rb')}
    elif content is not None:
        # This is to post a text content.
        files = {'file': content}

    # Send a http request with post method by requests.
    # Since boto doesn't support POST at make_request().
    url = "http://%s:%s/%s/" % (bucket.connection.host,
                                bucket.connection.port,
                                bucket.name)
    response = s3requests.post(url, data=form_fields, files=files)
    return response

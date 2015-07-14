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

"""Manage loading and return of test configuration settings."""

from os import environ as env

import boto

from ecstest import constants


def _env_to_bool(envname, default_value=0):
    envval = env.get(envname, default_value)
    try:
        return bool(int(envval))
    except ValueError:
        raise Exception("Unsupported env value: %s=%s" % (envname, envval))


def set_boto_config():
    """Set boto config"""
    if not boto.config.has_section('Boto'):
        boto.config.add_section('Boto')
    boto.config.set('Boto', 'num_retries',
                    env.get('ECSTEST_BOTO_NUM_RETRIES', '0'))
    boto.config.set('Boto', 'http_socket_timeout',
                    env.get('ECSTEST_BOTO_HTTP_SOCK_TMO', '5'))


def get_config():
    """Return a dictionary of configuration values."""

    return {
        'ADMIN_USERNAME': env.get('ECSTEST_ADMIN_USERNAME', 'username'),
        'ADMIN_PASSWORD': env.get('ECSTEST_ADMIN_PASSWORD', 'password'),
        'TOKEN': env.get('ECSTEST_TOKEN', None),
        'CONTROL_ENDPOINT': env.get(
            'ECSTEST_CONTROL_ENDPOINT', 'https://127.0.0.1:4443'
        ),
        'TOKEN_ENDPOINT': env.get(
            'ECSTEST_CONTROL_TOKEN_ENDPOINT', 'https://127.0.0.1:4443/login'
        ),
        'ALT_CONTROL_ENDPOINT': env.get(
            'ECSTEST_ALT_CONTROL_ENDPOINT',
            env.get('ECSTEST_CONTROL_ENDPOINT',
                    'https://127.0.0.1:4443')),
        'ALT_TOKEN_ENDPOINT': env.get(
            'ECSTEST_ALT_CONTROL_TOKEN_ENDPOINT',
            env.get('ECSTEST_CONTROL_TOKEN_ENDPOINT',
                    'https://127.0.0.1:4443/login'),
        ),
        'VERIFY_SSL': _env_to_bool('ECSTEST_VERIFY_SSL', 0),
        'REQUEST_TIMEOUT': float(env.get('ECSTEST_REQUEST_TIMEOUT', 15.0)),
        'TOKEN_FILENAME': env.get(
            'ECSTEST_TOKEN_FILENAME', '/tmp/ecstest.token'
        ),
        'CACHE_TOKEN': _env_to_bool('ECSTEST_CACHE_TOKEN', 1),
        'AUTH_TOKEN_MIN_LENGTH': env.get('ECSTEST_AUTH_TOKEN_MIN_LENGTH', 1),
        'AUTH_TOKEN_MAX_LENGTH': env.get('ECSTEST_AUTH_TOKEN_MAX_LENGTH', 512),
        'NAMESPACE': env.get('ECSTEST_NAMESPACE', 'namespace1'),
        'MAX_LOGIN_TIME': env.get('ECSTEST_MAX_LOGIN_TIME', 3),
        'ACCESS_SSL': _env_to_bool('ECSTEST_ACCESS_SSL', 0),
        'ACCESS_SERVER': env.get('ECSTEST_ACCESS_SERVER', 'localhost'),
        'ALT_ACCESS_SERVER': env.get(
            'ECSTEST_ALT_ACCESS_SERVER',
            env.get('ECSTEST_ACCESS_SERVER', 'localhost')
        ),
        'ACCESS_PORT': int(env.get('ECSTEST_ACCESS_PORT', 3128)),
        'ACCESS_KEY': env.get('ECSTEST_ACCESS_KEY', 'mykey'),
        'ACCESS_SECRET': env.get('ECSTEST_ACCESS_SECRET', 'mysecret'),
        'ALT_ACCESS_KEY': env.get(
            'ECSTEST_ALT_ACCESS_KEY',
            env.get('ECSTEST_ACCESS_KEY', 'mykey')
        ),
        'ALT_ACCESS_SECRET': env.get(
            'ECSTEST_ALT_ACCESS_SECRET',
            env.get('ECSTEST_ACCESS_SECRET', 'mysecret')
        ),
        'VERBOSE_OUTPUT': _env_to_bool('ECSTEST_VERBOSE_OUTPUT', 0),
        'TEST_TARGET': env.get('ECSTEST_TEST_TARGET', constants.TARGET_AWSS3),
        'TEST_TYPE': env.get(
            'ECSTEST_TEST_TYPE', constants.TYPE_COMPATIBILITY
        ),
        'DNS_BUCKET_NAMING_CONVENTION': _env_to_bool(
            'ECSTEST_DNS_BUCKET_NAMING_CONVENTION', 0
        ),
        'NODES_PER_SITE': int(env.get('ECSTEST_NODES_PER_SITE', 1)),
        'RUN_DISABLED': _env_to_bool('ECSTEST_RUN_DISABLED'),
        'REUSE_BUCKET_NAME': env.get('ECSTEST_REUSE_BUCKET_NAME'),
    }

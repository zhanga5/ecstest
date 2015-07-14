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

import requests
from email.utils import formatdate
from requests.packages.urllib3.util import parse_url

from ecstest.logger import logger
from ecstest import constants
from ecstest import config
from ecstest import utils

cfg = config.get_config()


def get(url, access_key=None, secret_key=None, **kwargs):
    """Sends a GET request.
    :param url: URL for the new request, combined of
        scheme://host:port/path, not include query string
    :param access_key: access_key for signature usage,
        if none will use default.
    :param secret_key: secret_key for signature usage.
        if none will use default.
    :param **kwargs: Optional arguments that ``request`` takes.
    """
    return request('GET', url, access_key, secret_key, **kwargs)


def put(url, access_key=None, secret_key=None, **kwargs):
    """Sends a PUT request.
    :param url: URL for the new request, combined of
        scheme://host:port/path, not include query string
    :param access_key: access_key for signature usage,
        if none will use default.
    :param secret_key: secret_key for signature usage.
        if none will use default.
    :param **kwargs: Optional arguments that ``request`` takes.
    """
    return request('PUT', url, access_key, secret_key, **kwargs)


# POST method has form-fields including signature in it.
# So don't need to set header AUTHORIZATION again.
def post(url, **kwargs):
    """Sends a POST request.
    :param url: URL for the new request, combined of
        scheme://host:port/path, not include query string
    :param access_key: access_key for signature usage,
        if none will use default.
    :param secret_key: secret_key for signature usage.
        if none will use default.
    :param **kwargs: Optional arguments that ``request`` takes.
    """
    return requests.Session().post(url, **kwargs)


def head(url, access_key=None, secret_key=None, **kwargs):
    """Sends a HEAD request.
    :param url: URL for the new request, combined of
        scheme://host:port/path, not include query string
    :param access_key: access_key for signature usage,
        if none will use default.
    :param secret_key: secret_key for signature usage.
        if none will use default.
    :param **kwargs: Optional arguments that ``request`` takes.
    """
    # If there is a redirect, it does a GET on the destination,
    # not a HEAD, so disable it.
    kwargs.setdefault('allow_redirects', False)
    return request('HEAD', url, access_key, secret_key, **kwargs)


def options(url, access_key=None, secret_key=None, **kwargs):
    """Sends a OPTIONS request.
    :param url: URL for the new request, combined of
        scheme://host:port/path, not include query string
    :param access_key: access_key for signature usage,
        if none will use default.
    :param secret_key: secret_key for signature usage.
        if none will use default.
    :param **kwargs: Optional arguments that ``request`` takes.
    """
    return request('OPTIONS', url, access_key, secret_key, **kwargs)


def patch(url, access_key=None, secret_key=None, **kwargs):
    """Sends a PATCH request.
    :param url: URL for the new request, combined of
        scheme://host:port/path, not include query string
    :param access_key: access_key for signature usage,
        if none will use default.
    :param secret_key: secret_key for signature usage.
        if none will use default.
    :param **kwargs: Optional arguments that ``request`` takes.
    """
    return request('PATCH', url, access_key, secret_key, **kwargs)


def delete(url, access_key=None, secret_key=None, **kwargs):
    """Sends a DELETE request.
    :param url: URL for the new request, combined of
        scheme://host:port/path, not include query string
    :param access_key: access_key for signature usage,
        if none will use default.
    :param secret_key: secret_key for signature usage.
        if none will use default.
    :param **kwargs: Optional arguments that ``request`` takes.
    """
    return request('DELETE', url, access_key, secret_key, **kwargs)


def request(method, url, access_key, secret_key, **kwargs):
    """Sends request with different method
    This is to construct a whole headers by adding basic header
    e.g. Date/Authorization besides user defined.
    And also sort params by its name for signature.
    """
    if access_key is None:
        access_key = cfg['ACCESS_KEY']
    if secret_key is None:
        secret_key = cfg['ACCESS_SECRET']
    logger.debug('access_key: %s, secret_key: %s', access_key, secret_key)

    if 'headers' in kwargs:
        headers = kwargs['headers'].copy()
    else:
        headers = {}

    if not find_matching_headers(constants.DATE, headers):
        headers[constants.DATE] = formatdate(usegmt=True)

    string_to_sign = '%s\n' % method
    if find_matching_headers(constants.CONTENT_MD5, headers):
        string_to_sign += '%s\n' % headers[constants.CONTENT_MD5]
    else:
        string_to_sign += '\n'

    if find_matching_headers(constants.CONTENT_TYPE, headers):
        string_to_sign += '%s\n' % headers[constants.CONTENT_TYPE]
    else:
        string_to_sign += '\n'

    string_to_sign += headers[constants.DATE] + '\n'

    # Sort canonicalizedAmzHeaders by name
    amz_keys = [h for h in headers if h.lower().startswith('x-amz-')]
    amz_keys.sort()
    for key in amz_keys:
        string_to_sign += '%s:%s\n' % (key, headers[key].strip())

    canonicalized_resource = ''

    # The subresources that must be included
    # when constructing the CanonicalizedResource
    # for calculating signature.
    subresources = ['acl', 'lifecycle', 'location', 'logging',
                    'notification', 'partNumber', 'policy',
                    'requestPayment', 'torrent', 'uploadId',
                    'uploads', 'versionId', 'versioning',
                    'versions', 'website']

    _, _, _, _, path, _, _ = parse_url(url)

    if not path:
        path = '/'

    canonicalized_resource += path

    if 'params' in kwargs:
        params = kwargs['params'].copy()
    else:
        params = {}

    subresource_without_value = []
    subresource_to_sign = []

    # Sort subresource by name, otherwise signature will not match.
    # If the value of key in dict params is none, e.g. ?acl,
    # it will not be appended to query string by requests parsing.
    # So need to pick it up from params to query string by manual.
    params = sorted(params.items(), key=lambda d: d[0])
    for key, value in params:
        if key in subresources:
            # subresource has value
            if value is not None:
                subresource_to_sign.append('%s=%s' % (key, value))
            else:
                subresource_to_sign.append('%s' % key)
                subresource_without_value.append('%s' % key)
        else:
            if value is None:
                subresource_without_value.append('%s' % key)

    if subresource_to_sign:
        canonicalized_resource += '?'
        canonicalized_resource += '&'.join(subresource_to_sign)

    if subresource_without_value:
        url += '?'
        url += '&'.join(subresource_without_value)

    string_to_sign += canonicalized_resource
    logger.debug('string to sign:\n%s', string_to_sign)
    logger.debug('request url:\n%s', url)

    headers[constants.AUTHORIZATION] = 'AWS %s:%s' \
                                       % (access_key,
                                          utils.get_signature(secret_key,
                                                              string_to_sign))
    logger.debug('headers is ' + repr(headers))

    if 'verify' not in kwargs:
        kwargs['verify'] = False

    kwargs['timeout'] = cfg['REQUEST_TIMEOUT']
    kwargs['headers'] = headers
    logger.debug('kwargs headers is ' + repr(kwargs['headers']))
    kwargs['params'] = params
    logger.debug('kwargs params is ' + repr(kwargs['params']))

    session = requests.Session()
    response = session.request(method, url, **kwargs)
    return response


def find_matching_headers(name, headers):
    """
    Takes a specific header name and a dict of headers {"name": "value"}.
    Returns a list of matching header names, case-insensitive.
    """
    return [h for h in headers if h.lower() == name.lower()]

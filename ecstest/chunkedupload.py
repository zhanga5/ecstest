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

try:
    import httplib as hlib
except ImportError:
    import http.client as hlib

import time
import urllib

from boto.utils import find_matching_headers
from boto import UserAgent

from ecstest.logger import logger
from ecstest import constants
from ecstest import filehelper
from ecstest import s3requests
from ecstest.utils import get_signature


def upload_file(bucket, key_name, filename, chunk_size_list=None):
    '''
    Upload key contents of chunked transfer encoding from file.
    '''
    return _upload_chunk(bucket, key_name, filename, chunk_size_list)


def upload_strings(bucket, key_name, strings):
    '''
    :param strings: a list of string
    Upload key contents of chunked transfer encoding from strings.
    '''
    return _upload_chunk(bucket, key_name, content=strings)


def _upload_chunk(bucket, key_name,
                  filepath=None, chunk_size_list=None, content=None):
    '''
    Upload key contents of chunked transfer encoding
    from file or string content.
    '''
    headers = {}
    headers[constants.TRANSFER_ENCODING] = 'chunked'
    url = "http://%s:%s/%s/%s" % (bucket.connection.host,
                                  bucket.connection.port,
                                  bucket.name,
                                  key_name)
    if chunk_size_list is None:
        chunk_size_list = []
    else:
        # Do deep copy since this list will be changed
        # that may affect top level.
        chunk_size_list = chunk_size_list[:]

    data = ''

    # Upload chunk from file.
    # TODO: need to enhance when upload so large file, should use virtual file
    if filepath is not None:
        with open(filepath, 'rb') as fp:
            while True:
                chunk_size = _pick_chunk_size(chunk_size_list)
                if chunk_size > 0:
                    chunk = fp.read(chunk_size)
                    if not chunk:
                        break
                    data = _add_chunk_block(data, chunk)
                # It has no chance to send invalid chunk_size(such as 0 or -1)
                # to ECS, because file read will eat it.
                # So send the invalid size with test data directly to ECS,
                # to test the negative scenario.
                else:
                    data += '%x\r\n' % chunk_size
                    data += '1234567890\r\n'
    # Upload chunk from string.
    elif content is not None:
        for chunk in content:
            data = _add_chunk_block(data, chunk)

    data += '0\r\n'
    data += '\r\n'

    response = s3requests.put(url, data=data, headers=headers)

    return response


def _add_chunk_block(data, chunk):
    ''' Encode data for chunked uploads. More details please refer to:
    http://en.wikipedia.org/wiki/Chunked_transfer_encoding
    '''
    data += '%x\r\n' % len(chunk)
    data += chunk
    data += '\r\n'
    return data


def _pick_chunk_size(chunk_size_list):
    '''
    Pick the first size from chunk_size_list,
    Then delete the size picked.
    Use the default size if chunk_size_list is empty.
    TODO:should add env var config support to override this default size
    '''
    default_size = constants.ECS_100KB_OBJ_SIZE * 8
    if chunk_size_list:
        chunk_size = chunk_size_list.pop(0)
    else:
        chunk_size = default_size
    return chunk_size


def _make_request(bucket, method, request_resource, headers, data):
    '''
    Set http client and request typically for POST
    since boto doesn't support POST method.
    '''
    host = bucket.connection.host
    port = bucket.connection.port
    try:
        if bucket.connection.is_secure:
            http = hlib.HTTPSConnection(host, port)
        else:
            http = hlib.HTTPConnection(host, port)
        http.connect()
        http.putrequest(method, request_resource)
        for k, v in headers.items():
            http.putheader(k, v)
        http.endheaders()

        # TODO: should refine PseudoFile act as a file object
        if isinstance(data, filehelper.PseudoFile):
            data.send(http)
        else:
            http.send(data)
        resp = http.getresponse()
    except hlib.HTTPException as e:
        logger.exception('exception occur: %s ', e.message)
    except Exception as e:
        logger.exception('http request failed')
    finally:
        http.close()
    return resp


# TODO: need to implement chunk upload with pseudo file if has requirement.
def upload_pseudo_file(bucket, key_name, length,
                       chunk_size_list=None, **kwargs):
    '''Set contents of key from pseudofile with large size.
    '''
    if 'headers' in kwargs:
        headers = kwargs['headers'].copy()
    else:
        headers = {}

    if 'query_args' in kwargs:
        query_args = kwargs['query_args']
    else:
        query_args = None

    # Overwrite user-supplied user-agent.
    for header in find_matching_headers('User-Agent', headers):
        del headers[header]
    headers['User-Agent'] = UserAgent

    # Overwrite user-supplied date.
    for header in find_matching_headers('Date', headers):
        del headers[header]

    utc_time = time.strftime('%a, %d %b %Y %H:%M:%S GMT',
                             time.localtime(time.time()))
    headers['Date'] = utc_time

    hash_string = 'PUT' + '\n' + '\n' + '\n' + utc_time + '\n'

    request_resource = '/' + urllib.quote(bucket.name, '') + \
                       '/' + urllib.quote(key_name, '')

    if query_args:
        request_resource += '?' + query_args
    hash_string += request_resource

    signature = get_signature(bucket.connection.provider.secret_key,
                              hash_string)
    authorization = 'AWS' + ' ' + bucket.connection.provider.access_key + \
                    ":" + signature

    pseudofile = filehelper.PseudoFile(length)
    if not find_matching_headers('Content-Length', headers):
        headers['Content-Length'] = length

    if not find_matching_headers('Authorization', headers):
        headers['Authorization'] = authorization

    return pseudofile, _make_request(bucket, 'PUT', request_resource,
                                     headers, pseudofile)

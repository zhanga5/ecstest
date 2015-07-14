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

import inspect
import uuid
import string
import os

from ecstest import config
from ecstest import constants

cfg = config.get_config()

def get_unique_bucket_name_prefix(depth=2):
    '''
    idea is to have caller file name and line number as part of the bucket name, so that we 
    could easily identify who created this bucket.
    '''
    # get caller function frame info
    callerframerecord = inspect.stack()[depth]
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)
    # most callers will have file name like foo_test.py. we just need the foo part
    fn = os.path.basename(info.filename)
    index = fn.rfind('_test.py')
    if index != -1:
        fn = fn[0:index]
    # some simple filtering on unwanted characters
    return fn.replace(' ', '').replace('.', '').replace('_','-').lower() + str(info.lineno)

def get_unique_bucket_name(prefix = None):
    if not prefix:
        prefix = get_unique_bucket_name_prefix()

    return 'ecstest-' + prefix + '-' + str(uuid.uuid4())

def get_shortest_bucket_name_list():
    if cfg['DNS_BUCKET_NAMING_CONVENTION']:
        return get_shortest_dns_bucket_name_list()
    else:
        return get_shortest_expand_bucket_name_list()

def get_longest_bucket_name_list():
    if cfg['DNS_BUCKET_NAMING_CONVENTION']:
        return get_longest_dns_bucket_name_list()
    else:
        return get_longest_expand_bucket_name_list()

def get_bucket_name_with_special_symbol_list():
    if cfg['DNS_BUCKET_NAMING_CONVENTION']:
        return get_dns_bucket_name_with_special_symbol_list()
    else:
        return get_expand_bucket_name_with_special_symbol_list()

def get_shortest_dns_bucket_name_list():
    return [
        'abc',
        '123',
        'ab1',
        'a12',
        'a-1',
    ]

def get_shortest_expand_bucket_name_list():
    return [
        'abc',
        'ABC',
        '123',
        'aA1',
        'a.B',
        'a-1',
        'A_2',
        'a.-',
        'a._',
        'a-_',
        '.-A',
        '._A',
        '-_A',
        '.-_',
    ]

def get_shortest_ecs_bucket_name_list():
    return [
        'c',
        'D',
        '3',
        '-',
        '_',
]

def get_longest_dns_bucket_name_list():
    longest_len = constants.LONGEST_DNS_BUCKET_NAME_LENGTH

    prefix_str = 'a.0-'
    prefix_len = len(prefix_str)
    uuid_str = str(uuid.uuid4())
    uuid_len = len(uuid_str)
    left_len = longest_len - prefix_len - uuid_len
    return [
        prefix_str + uuid_str + left_len * 'e',
    ]

def get_longest_expand_bucket_name_list():
    longest_len = constants.LONGEST_EXPAND_BUCKET_NAME_LENGTH

    prefix_str = 'aA0.-_'
    prefix_len = len(prefix_str)
    uuid_str = str(uuid.uuid4())
    uuid_len = len(uuid_str)
    left_len = longest_len - prefix_len - uuid_len
    return [
        prefix_str + uuid_str + left_len * 'e',
    ]

def get_longest_ecs_bucket_name_list():
    longest_len = constants.LONGEST_ECS_BUCKET_NAME_LENGTH

    prefix_str = 'aA0.-_'
    prefix_len = len(prefix_str)
    uuid_str = str(uuid.uuid4())
    uuid_len = len(uuid_str)
    left_len = longest_len - prefix_len - uuid_len
    return [
        prefix_str + uuid_str + left_len * 'e',
    ]

def get_dns_bucket_name_with_special_symbol_list():
    uuid_str = str(uuid.uuid4())

    return  [
        # prefix special symbol
        's' + '.' + uuid_str,
        's' + '-' + uuid_str,

        # suffix special symbol
        uuid_str + '.' + 'e',
        uuid_str + '-' + 'e',
    ]

def get_expand_bucket_name_with_special_symbol_list():
    uuid_str = str(uuid.uuid4())

    return  [
        # prefix special symbol
        '.' + uuid_str,
        '-' + uuid_str,
        '_' + uuid_str,
        '..' + uuid_str,
        '--' + uuid_str,
        '__' + uuid_str,
        '.-' + uuid_str,
        '._' + uuid_str,
        '-_' + uuid_str,
        '.-_' + uuid_str,

        # suffix special symbol
        # On Amazon s3. the bucket name can not end with '.'
        uuid_str + '-',
        uuid_str + '_',
        uuid_str + '--',
        uuid_str + '__',
        uuid_str + '.-',
        uuid_str + '._',
        uuid_str + '-_',
        uuid_str + '.-_',
    ]

def get_ecs_bucket_name_with_special_symbol_list():
    uuid_str = str(uuid.uuid4())

    return  [
        # Cannot start with a period, end with a period

        # prefix special symbol
        '-' + uuid_str,
        '_' + uuid_str,
        '-.' + uuid_str,
        '--' + uuid_str,
        '-_' + uuid_str,
        '_.' + uuid_str,
        '_-' + uuid_str,
        '__' + uuid_str,
        '_.-' + uuid_str,


        # suffix special symbol
        uuid_str + '-',
        uuid_str + '_',
        uuid_str + '--',
        uuid_str + '__',
        uuid_str + '.-',
        uuid_str + '._',
        uuid_str + '-_',
        uuid_str + '.-_',
    ]

def get_valid_name_list():
    if cfg['DNS_BUCKET_NAMING_CONVENTION']:
        return get_valid_dns_name_list()
    else:
        return get_valid_expand_name_list()

def get_invalid_char_name_list():
    if cfg['DNS_BUCKET_NAMING_CONVENTION']:
        return get_invalid_char_dns_name_list()
    else:
        return get_invalid_char_expand_name_list()

def get_invalid_too_short_name_list():
    return ['a', 'ab']

def get_invalid_too_long_name_list():
    if cfg['DNS_BUCKET_NAMING_CONVENTION']:
        return ['a'*64]
    else:
        return ['a'*256]

def get_valid_dns_name_list():
    uuid_str = str(uuid.uuid4())
    return [
        'myawsbucket' + uuid_str,
        'my.aws.bucket' + uuid_str,
        'myawsbucket.1' + uuid_str,
        '192.168.5.1-192.168.5.3' + uuid_str,
        '021-12345678' + uuid_str,
        string.ascii_lowercase  + '.' + string.digits + '-' + 'e'
    ]

def get_valid_expand_name_list():
    return []

def get_valid_ecs_name_list():
    uuid_str = str(uuid.uuid4())
    return [
        'myawsbucket' + uuid_str,
        'myawsbucket.TEST' + uuid_str,
        'myawsbucket_1' + uuid_str,
        '021-12345678' + uuid_str,
        string.ascii_letters  + '.-_' + string.digits,
    ]

def get_invalid_char_dns_name_list():
    invalid_chars = [
        '\x00', '\x1F', # control chars
        '\x20', '\x2C', # from ' ' to ','
        '\x2e',         # '.'
                        # '/' changes the request to an object request
        '\x3A', '\x40', # from ':' to '@'
        '\x41', '\x5A', # form 'A' to 'Z'
        '\x5B', '\x5E', # from '[' to '^'
        '\x5F',         # '_'
        '\x60',         # '`'
        '\x7B', '\x7F', # from '{' to DEL
        '\x80', '\xFF'] # from 128 to 255

    uuidstr = str(uuid.uuid4())
    return ['a-%%%02x-%s' % (ord(c), uuidstr) for c in invalid_chars]

def get_invalid_char_expand_name_list():
    invalid_chars = [
        '\x00', '\x1F', # control chars
        '\x20', '\x2C', # from ' ' to ','
                        # '/' changes the request to an object request
        '\x3A', '\x40', # from ':' to '@'
        '\x5B', '\x5E', # from '[' to '^'
                        # '\x5F' is '_', valid here
        '\x60',         # '`'
        '\x7B', '\x7F', # from '{' to DEL
        '\x80', '\xFF'] # from 128 to 255

    uuidstr = str(uuid.uuid4())
    return ['a-%%%02x-%s' % (ord(c), uuidstr) for c in invalid_chars]

def get_invalid_uppercase_letter_name_list():
    return ['abc%s-%s' % ('A', str(uuid.uuid4())),
            'abc%s-%s' % ('Z', str(uuid.uuid4()))]

def get_invalid_dot_hyphen_name_list():
    return ['.abc', 'abc.', '-abc', 'abc-']

def get_invalid_continuous_dot_name_list():
    # On Amazon s3. the bucket name 'ab--c' is valid
    return ['ab..c', 'ab.-c', 'ab-.c', 'ab__c', 'ab_.-c', 'ab-_c', 'ab_-c']

def get_invalid_ip_name():
    # On Amazon s3. the bucket name '192.168.5.1-192.168.5.3'
    # '021-12345678' are valid
    return ['192.168.5.4']

def get_invalid_dot_continuous_ecs_name_list():
    return ['.abc', 'abc.', 'ab..c']

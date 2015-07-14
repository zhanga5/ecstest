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

import binascii
import hashlib
import hmac
import re
import requests
import time
import uuid

from boto.s3.key import Key

from ecstest.controlplane import usermgmt
from ecstest.logger import logger
from ecstest import config
from ecstest import constants


cfg = config.get_config()


def mktime_from_str(time_string, time_format="%a, %d %b %Y %H:%M:%S %Z"):
    '''transform time string got from head to seconds since the epoch
    '''
    return int(time.mktime(time.strptime(time_string, time_format)))


def delete_keys(bucket, target):
    '''
    Delete all keys at the bucket with
    different target like S3/fakes3/ecs.
    '''
    key_list = []
    while True:
        # The most keys of S3/fakes3/ecs returned
        # by each time is 1000.
        # Under fakes3, get_all_versions() returns a key_list
        # which cause strange error when delete, so deal with it separately
        if target == constants.TARGET_FAKES3:
            key_list = bucket.get_all_keys()
            if len(key_list) == 0:
                break
            # Fakes3 doesn't support delete_keys() and delete_key() finely.
            # So add a loop to delete one by one.
            for key in key_list:
                Key(bucket, key.name).delete()
        else:
            key_list = bucket.get_all_keys()
            if len(key_list) == 0:
                break
            bucket.delete_keys(key_list)


def _get_vdc_list():
    '''
    Generate VDC list in ECS
    '''
    # get VDC list with ECS rest API
    vdc_list = []
    admin = usermgmt.UserAdmin()
    auth_token = admin.login()

    url = cfg['CONTROL_ENDPOINT'] + '/object/vdcs/vdc/list'
    headers = {
        'Content-Type': 'application/xml',
        'X-SDS-AUTH-TOKEN': auth_token
    }

    try:
        session = requests.Session()
        response = session.get(url, headers=headers, verify=False)
        content = response.text

        # filter the response body to get the interVdcEndPoints for each VDC
        pat = re.compile(r'<interVdcEndPoints>([\d., ]*)</interVdcEndPoints>')

        # a list of VDC will be like as below, each item is a string type.
        # [u'172.29.3.148, 172.29.3.149, 172.29.3.150, 172.29.3.151',
        #  u'172.29.3.212, 172.29.3.213, 172.29.3.214, 172.29.3.215']
        vdc_list = pat.findall(content.replace('\n', ''))

        # return a VDC list with each VDC item is a list of nodes
        return [[ip.strip() for ip in vdc.split(',')] for vdc in vdc_list]

    finally:
        # leak auth token
        if admin.client.token:
            logger.debug('release the auth token')
            admin.logout()


def generate_node_list(num=None):
    '''Generate a list of nodes
    All the nodes appear in this list as evenly as possible
    '''
    if num is None:
        num = constants.DEFAULT_THREAD_NUMBER

    node_list = []

    # make sure ECS runtest cfg file includes below item:
    # export ECSTEST_TEST_TARGET='ECS'
    if cfg['TEST_TARGET'] == constants.TARGET_ECS:
        # if the test target is ECS, then get the node list from ECS REST API
        vdc_list = _get_vdc_list()
        logger.debug('get VDC list: %s', vdc_list)

        # In case that a VDC contains different node number,
        # this variable identifies a VDC with max nodes number.
        max_len_vdc = max([len(vdc) for vdc in vdc_list])

        # use below parsing logic to return a node list with required number
        for i in range(max_len_vdc):
            for j in range(len(vdc_list)):
                if i < len(vdc_list[j]):
                    node_list.append(vdc_list[j][i])
                    if len(node_list) == num:
                        return node_list
    else:
        # if the test target is AWSS3 or FAKES3, just use them literally
        nodes = [cfg['ACCESS_SERVER'], cfg['ALT_ACCESS_SERVER']]

        while num > 0:
            items = min(num, len(nodes))
            node_list.extend(nodes[0:items])
            num -= items

    return node_list


def get_content_md5(data):
    '''get the base64-encoded 128-bit MD5 digest of the data.'''
    md5_digest = hashlib.md5(data)
    return binascii.b2a_base64(md5_digest.digest()).strip('\n')[:]


def get_signature(secret_key, string_to_sign):
    '''
    Get the signature for authorization
    '''
    hashed = hmac.new(secret_key.encode('utf-8'),
                      string_to_sign.encode('utf-8'), hashlib.sha1)
    return binascii.b2a_base64(hashed.digest()).strip('\n')


def get_elements_from_xml(elementname, data):
    '''get the element value from xml response
    and return a list of all elements' value.
    '''
    pattern = re.compile(r'<%s>(.*?)</%s>' % (elementname, elementname))
    return pattern.findall(data.replace('\n', ''))


class AltUser(object):
    '''Represent an alt user in ECS or AWS'''
    cfg = config.get_config()

    def __init__(self):
        # Create one user for ecs
        # Need to export ECSTEST_TEST_TARGET='ECS'
        # for ECS runtest cfg file
        if self.cfg['TEST_TARGET'] == constants.TARGET_ECS:
            self.username = uuid.uuid4().hex
            logger.debug('username is ' + self.username)

            self.user_admin = usermgmt.UserAdmin()
            user_info = self.user_admin.create_user(self.username)
            logger.debug('user_info is ' + str(user_info))

            self.secret_key = self.user_admin.create_secret_key(self.username)
            logger.debug('secret_key is ' + str(self.secret_key))
        # Get another user info from config for aws
        # Need to export ECSTEST_ALT_ACCESS_KEY
        # and ECSTEST_ALT_ACCESS_SECRET
        # for AWS runtest cfg file.
        elif self.cfg['TEST_TARGET'] == constants.TARGET_AWSS3:
            self.username = self.cfg['ALT_ACCESS_KEY']
            logger.debug('username is ' + self.username)
            self.secret_key = self.cfg['ALT_ACCESS_SECRET']
            logger.debug('secret_key is ' + self.secret_key)
        else:
            raise Exception('Can not create another user!')

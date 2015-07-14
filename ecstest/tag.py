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

"""Predefined Tags for applying to tests"""

# components under test
AUTH = 'auth'
BUCKET_MGMT = 'bucketmgmt'
CONTROL_PLANE = 'controlplane'
DATA_PLANE = 'dataplane'
OBJECT_IO = 'objectio'
OBJECT_USER_MGMT = 'objectusermgmt'
KEY_MGMT = 'keymgmt'
SECRET_KEY_MGMT = 'secretkeymgmt'
VERSION = 'version'

# test duration, anything more than 30 sec could be considered as long.
LONG = 'long'

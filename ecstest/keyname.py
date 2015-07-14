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

import uuid

def get_unique_key_name():
    return 'key-' + str(uuid.uuid4())

def get_unichr_sequence(begin, end):
    '''
    Get a key name with consecutive string sequence from begin to end
    '''
    seq = u''
    for i in range(begin, end):
        seq += unichr(i)
    return seq


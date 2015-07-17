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

from boto.s3.bucket import Bucket
from nose.plugins.attrib import attr
from nose.tools import eq_ as eq

from ecstest import bucketname
from ecstest import keyname
from ecstest import tag
from ecstest import testbase
from ecstest import utils
from ecstest.dec import not_supported
from ecstest.dec import triage
from ecstest.logger import logger


@attr(tags=[tag.DATA_PLANE, tag.OBJECT_IO])
class TestObjectList(testbase.EcsDataPlaneTestBase):
    """
    Post several objects and list them within a bucket
    """
    def setUp(self):
        super(TestObjectList, self).setUp(create_bucket=True)

    def tearDown(self):
        super(TestObjectList, self).tearDown()

    def _create_bucket(self, bucket_name=None):
        """
        To create bucket with bucket_name
        """
        if bucket_name is None:
            bucket_name = bucketname.get_unique_bucket_name()

        logger.debug("Create bucket: %s", bucket_name)
        bucket = self.data_conn.create_bucket(bucket_name)
        eq(isinstance(bucket, Bucket), True)

        return bucket

    def _create_keys(self, keys=[]):
        """
        Populate a (specified or new) bucket with objects with
        specified names (and contents identical to their names).
        """
        for s in keys:
            key = self.bucket.new_key(s)
            key.set_contents_from_string(s)

    @triage
    # port from test case: test_bucket_list_distinct() of https://github.com/
    #   ceph/s3-tests/blob/master/s3tests/functional/test_s3.py
    def test_object_list_from_distinct_bucket(self):
        """
        operation: list
        assertion: distinct buckets have different contents
        """
        bucket1 = self._create_bucket()
        bucket2 = self._create_bucket()

        name = keyname.get_unique_key_name()
        key = bucket1.new_key(name)
        key.set_contents_from_string(name)

        l = bucket2.list()
        l = list(l)
        eq(l, [])

        for bucket in [bucket1, bucket2]:
            logger.debug("delete all keys in bucket: %s", bucket.name)
            utils.delete_keys(bucket, self.target)
            self.data_conn.delete_bucket(bucket.name)

    @triage
    # ecs marker issue: the response Keys contain the marker ,
    #   that is not consistent with aws-s3 which don't contain the marker.
    # fakes3 MaxKeys issue: the response MaxKeys always be 1000
    #   no matter what the request max_keys are.
    @not_supported('fakes3', 'ecs')  # fakes3 MaxKeys issue, ecs marker issue
    # port from test case: test_bucket_list_many() of https://github.com/
    #   ceph/s3-tests/blob/master/s3tests/functional/test_s3.py
    def test_object_list_many(self):
        """
        operation: list
        assertion: pagination w/max_keys=2, no marker
        """
        keyname1 = keyname.get_unique_key_name()
        keyname2 = keyname.get_unique_key_name()
        keyname3 = keyname.get_unique_key_name()

        self._create_keys(keys=[keyname1, keyname2, keyname3])

        # bucket.list() is high-level and will not let us set max-keys,
        # using it would require using >1000 keys to test, and that would
        # be too slow; use the lower-level call bucket.get_all_keys()
        # instead

        l = self.bucket.get_all_keys(max_keys=2)
        eq(len(l), 2)
        eq(l.is_truncated, True)
        names = [e.name for e in l]
        eq(names, [keyname1, keyname2])

        l = self.bucket.get_all_keys(max_keys=2, marker=names[-1])
        eq(len(l), 1)
        eq(l.is_truncated, False)
        names = [e.name for e in l]
        eq(names, [keyname3])

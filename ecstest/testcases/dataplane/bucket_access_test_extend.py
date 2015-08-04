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
from boto.exception import S3ResponseError
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


def _assert_raises(excClass, callableObj, *args, **kwargs):
    """
    like unittest.TestCase.assertRaises, but return the exception.
    """
    try:
        callableObj(*args, **kwargs)
    except excClass as e:
        return e
    else:
        if hasattr(excClass, '__name__'):
            excName = excClass.__name__
        else:
            excName = str(excClass)
        raise AssertionError("%s not raised" % excName)


def _create_keys(bucket, keys=[]):
    """
    Populate a (specified or new) bucket with objects with
    specified names (and contents identical to their names).
    """
    for s in keys:
        key = bucket.new_key(s)
        key.set_contents_from_string(s)


@attr(tags=[tag.DATA_PLANE, tag.BUCKET_ACCESS])
class TestBucketAccess(testbase.EcsDataPlaneTestBase):
    """
    Access a bucket with several conditions and test the result of the response
    """

    def setUp(self):
        super(TestBucketAccess, self).setUp()
        self.bucket_list = []

    def tearDown(self):
        for bucket in self.bucket_list:
            try:
                logger.debug("delete all keys in bucket: %s", bucket.name)
                utils.delete_keys(bucket, self.target)
                self.data_conn.delete_bucket(bucket.name)
            except Exception as err:
                logger.warn("Delete bucket exception: %s", str(err))
        super(TestBucketAccess, self).tearDown()

    def _create_bucket(self, bucket_name=None):
        """
        To create bucket with bucket_name
        """
        if bucket_name is None:
            bucket_name = bucketname.get_unique_bucket_name()

        logger.debug("Create bucket: %s", bucket_name)
        bucket = self.data_conn.create_bucket(bucket_name)
        self.bucket_list.append(bucket)
        eq(isinstance(bucket, Bucket), True)

        return bucket

    @triage
    # port from test case: test_bucket_notexist() of https://
    #   github.com/ceph/s3-tests/blob/master/s3tests/functional/test_s3.py
    def test_bucket_not_exist(self):
        """
        operation: get a non-existent bucket
        assertion: fails with 404 error
        """
        # generate a (hopefully) unique, not-yet existent bucket name
        bucket_name = bucketname.get_unique_bucket_name()

        e = _assert_raises(S3ResponseError,
                           self.data_conn.get_bucket,
                           bucket_name)

        eq(e.status, 404)
        eq(e.reason, 'Not Found')
        eq(e.error_code, 'NoSuchBucket')

    @triage
    # fakes3 return: '500 Internal Server Error'
    @not_supported('fakes3')
    # port from test case: test_bucket_delete_notexist() of https://
    #   github.com/ceph/s3-tests/blob/master/s3tests/functional/test_s3.py
    def test_bucket_delete_not_exist(self):
        """
        operation: delete a non-existent bucket
        assertion: fails with 404 error
        """
        bucket_name = bucketname.get_unique_bucket_name()

        e = _assert_raises(S3ResponseError,
                           self.data_conn.delete_bucket,
                           bucket_name)
        eq(e.status, 404)
        eq(e.reason, 'Not Found')
        eq(e.error_code, 'NoSuchBucket')

    @triage
    # fakes3 return: '500 Internal Server Error'
    @not_supported('fakes3')
    # port from test case: test_bucket_delete_nonempty() of https://
    #   github.com/ceph/s3-tests/blob/master/s3tests/functional/test_s3.py
    def test_bucket_delete_not_empty(self):
        """
        operation: delete a non-empty bucket
        assertion: fails with 404 error
        """
        bucket = self._create_bucket()

        # fill up bucket
        key_name = keyname.get_unique_key_name()
        key = bucket.new_key(key_name)
        key.set_contents_from_string(key_name)

        # try to delete
        e = _assert_raises(S3ResponseError, bucket.delete)
        eq(e.status, 409)
        eq(e.reason, 'Conflict')
        eq(e.error_code, 'BucketNotEmpty')

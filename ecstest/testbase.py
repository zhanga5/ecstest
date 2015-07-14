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

import shutil
import tempfile
import testtools

from boto.s3.connection import S3Connection
from boto.s3.connection import OrdinaryCallingFormat

from ecstest import bucketname
from ecstest import client
from ecstest import config
from ecstest import constants
from ecstest import utils
from ecstest.extensions import matchers
from ecstest.logger import logger


class EcsTestBase(testtools.TestCase):
    cfg = config.get_config()

    """Generic TestBase class. Shall not use it but one of its subclass
    """
    def setUp(self):
        super(EcsTestBase, self).setUp()

    def assertJsonSchema(self, expected, observed, message=''):
        """Assert that 'expected' is equal to 'observed'.
        :param expected: The expected value.
        :param observed: The observed value.
        :param message: An optional message to include in the error.
        """
        matcher = matchers.JsonSchemaMatcher(expected)
        self.assertThat(observed, matcher, message)


class EcsControlPlaneTestBase(EcsTestBase):
    """Subclass for testing control plane
    """

    @classmethod
    def setUpClass(cls):
        super(EcsControlPlaneTestBase, cls).setUpClass()

        cls.client = cls.get_client()

        # Peform login so that the requests in each test class
        # are authenticated.
        cls.client.make_login_request()

    @classmethod
    def tearDownClass(cls):
        super(EcsControlPlaneTestBase, cls).tearDownClass()

        # This call is important, because we want to make sure and release the
        # token back to ECS; there is a limit on the number of active tokens.
        if cls.client.token:
            cls.client.make_logout_request()

    @classmethod
    def get_client(cls, is_alt=False):
        cfg = cls.cfg

        if is_alt:
            ecs_endpoint = cfg['ALT_CONTROL_ENDPOINT']
            token_endpoint = cfg['ALT_TOKEN_ENDPOINT']
        else:
            ecs_endpoint = cfg['CONTROL_ENDPOINT']
            token_endpoint = cfg['TOKEN_ENDPOINT']

        controlplane_client = client.EcsControlPlaneClient(
            username=cfg['ADMIN_USERNAME'],
            password=cfg['ADMIN_PASSWORD'],
            token=cfg['TOKEN'],
            ecs_endpoint=ecs_endpoint,
            token_endpoint=token_endpoint,
            verify_ssl=cfg['VERIFY_SSL'],
            token_filename=cfg['TOKEN_FILENAME'],
            request_timeout=cfg['REQUEST_TIMEOUT'],
            cache_token=cfg['CACHE_TOKEN']
        )

        return controlplane_client


class EcsDataPlaneTestBase(EcsTestBase):
    """Subclass for testing data plane
    """
    def setUp(self,
              create_tmpdir=False,
              create_bucket=False,
              allow_reuse_bucket=True):
        super(EcsDataPlaneTestBase, self).setUp()

        config.set_boto_config()

        cfg = self.cfg

        self.target = cfg['TEST_TARGET']
        if self.target not in constants.VALID_TARGETS:
            raise Exception('invalid test targets')

        self.data_conn = self.get_conn(host=cfg['ACCESS_SERVER'])

        self.alt_data_conn = self.get_conn(host=cfg['ALT_ACCESS_SERVER'])

        if create_tmpdir:
            self.__tmpdir = tempfile.mkdtemp(dir='/var/tmp')
            self.tmpdir = self.__tmpdir
            logger.debug("tmpdir %s was created.", self.tmpdir)
        else:
            self.__tmpdir = None

        if create_bucket:
            # 1 when test case allows to reuse bucket name and
            # env variable ECSTEST_REUSE_BUCKET_NAME is set, reuse name
            # 2 all rest situation to use new name.
            self.allow_reuse_bucket_flag = \
                allow_reuse_bucket is True and \
                self.cfg['REUSE_BUCKET_NAME'] is not None
            if self.allow_reuse_bucket_flag is True:
                self._reuse_bucket()
            else:
                prefix = bucketname.get_unique_bucket_name_prefix()
                self.__bucket_name = bucketname.get_unique_bucket_name(prefix)
                self.bucket_name = self.__bucket_name
                logger.debug("bucket name: %s", self.bucket_name)
                self.__bucket = \
                    self.data_conn.create_bucket(self.__bucket_name)
            self.bucket = self.__bucket
        else:
            self.__bucket = None

    def _reuse_bucket(self):
        '''
        At first, create a new bucket for reuse.
        In other cases, reuse the bucket.
        '''
        # Need to export ECSTEST_REUSE_BUCKET_NAME
        # to get an unique bucket name for reuse.
        # Otherwise, it will use a default name in config.py
        self.__bucket_name = self.cfg['REUSE_BUCKET_NAME']
        self.bucket_name = self.__bucket_name
        try:
            self.__bucket = self.data_conn.get_bucket(self.__bucket_name)
        except:
            # Ignore exception here.
            # It will create a new bucket.
            logger.debug("create bucket %s for reuse", self.__bucket_name)
            self.__bucket = self.data_conn.create_bucket(self.__bucket_name)

    def tearDown(self):
        if self.__tmpdir is not None:
            logger.debug("delete tmpdir: %s", self.__tmpdir)
            shutil.rmtree(self.__tmpdir)
            self.__tmpdir = None

        if self.__bucket is not None:
            logger.debug("delete all keys in bucket: %s", self.__bucket_name)
            # Sometime the bucket just disappears
            # Since this is the tearDown() function, just ignore it
            # Case: object_post_test.py:TestObjectPost.test_post_object_with_special_valid_name
            utils.delete_keys(self.__bucket, self.target)
            if self.allow_reuse_bucket_flag is True:
                logger.debug("reuse bucket will not be deleted")
            else:
                self.data_conn.delete_bucket(self.__bucket_name)

        super(EcsDataPlaneTestBase, self).tearDown()

    cfg = config.get_config()

    def get_conn(self,
                 aws_access_key_id=cfg['ACCESS_KEY'],
                 aws_secret_access_key=cfg['ACCESS_SECRET'],
                 is_secure=cfg['ACCESS_SSL'],
                 port=cfg['ACCESS_PORT'],
                 host=cfg['ACCESS_SERVER'],
                 calling_format=OrdinaryCallingFormat()):

        dataplane_conn = S3Connection(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            is_secure=is_secure,
            port=port,
            host=host,
            calling_format=calling_format)

        return dataplane_conn

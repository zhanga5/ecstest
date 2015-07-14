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

import datetime
import isodate
import re
import uuid
import threading
import email.utils
from nose.plugins.attrib import attr
from boto.s3.key import Key
from boto.exception import S3ResponseError
from nose.tools import eq_ as eq
from ecstest import tag, testbase, constants, bucketname
from ecstest.logger import logger
from ecstest import keyname
from ecstest import utils
from ecstest.dec import triage
from ecstest.dec import not_supported
from ecstest.dec import known_issue


def _get_keys_prefixes(li):
    """
    figure out which of the strings in a list are actually keys
    return lists of strings that are (keys) and are not (prefixes)
    """
    keys = [x for x in li if isinstance(x, Key)]
    prefixes = [x for x in li if not isinstance(x, Key)]
    return (keys, prefixes)


def _compare_dates(iso_datetime, http_datetime):
    """
    compare an iso date and an http date, within an epsilon
    """
    date = isodate.parse_datetime(iso_datetime)

    pd = email.utils.parsedate_tz(http_datetime)
    tz = isodate.tzinfo.FixedOffset(0, pd[-1]/60, 'who cares')
    date2 = datetime.datetime(*pd[:6], tzinfo=tz)

    # our tolerance
    minutes = 5
    acceptable_delta = datetime.timedelta(minutes=minutes)
    assert abs(date - date2) < acceptable_delta, \
        ("Times are not within {minutes} minutes of each other: "
         + "{date1!r}, {date2!r}").format(
            minutes=minutes,
            date1=iso_datetime,
            date2=http_datetime,
            )


def assert_raises(excClass, callableObj, *args, **kwargs):
    """
    Like unittest.TestCase.assertRaises, but returns the exception.
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


def validate_object_list(bucket, prefix, delimiter, marker, max_keys,
                         is_truncated, check_objs, check_prefixes,
                         next_marker):
    li = bucket.get_all_keys(delimiter=delimiter, prefix=prefix,
                             max_keys=max_keys, marker=marker)

    eq(li.is_truncated, is_truncated)
    eq(li.next_marker, next_marker)

    (keys, prefixes) = _get_keys_prefixes(li)

    eq(len(keys), len(check_objs))
    eq(len(prefixes), len(check_prefixes))

    objs = [e.name for e in keys]
    eq(objs, check_objs)

    prefix_names = [e.name for e in prefixes]
    eq(prefix_names, check_prefixes)

    return li.next_marker


@attr(tags=[tag.DATA_PLANE, tag.OBJECT_IO])
class TestObjectList(testbase.EcsDataPlaneTestBase):
    '''Post several objects and list them within a bucket
    '''
    def setUp(self):
        super(TestObjectList, self).setUp(create_bucket=True)
        self.key_list = []
        self.lock = threading.Lock()

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
    def test_object_list_from_distinct_bucket(self):
        """
        operation: list
        assertion: distinct buckets have different contents
        """
        bucket1 = self._create_bucket()
        bucket2 = self._create_bucket()

        key = bucket1.new_key('asdf')
        key.set_contents_from_string('asdf')
        l = bucket2.list()
        l = list(l)
        eq(l, [])

        for bucket in [bucket1, bucket2]:
            logger.debug("delete all keys in bucket: %s", bucket.name)
            utils.delete_keys(bucket, self.target)
            self.data_conn.delete_bucket(bucket.name)

    @triage
    # ecs marker issue: the response Keys contain the marker ,
    #   what is not consistent with aws-s3 which don't contain the marker.
    # fakes3 MaxKeys issue: the response MaxKeys always is 1000
    #   no matter what the request max_keys are.
    @not_supported('fakes3', 'ecs')  # fakes3 MaxKeys issue, ecs marker issue
    def test_object_list_many(self):
        """
        operation: list
        assertion: pagination w/max_keys=2, no marker
        """
        self._create_keys(keys=['foo', 'bar', 'baz'])

        # bucket.list() is high-level and will not let us set max-keys,
        # using it would require using >1000 keys to test, and that would
        # be too slow; use the lower-level call bucket.get_all_keys()
        # instead

        l = self.bucket.get_all_keys(max_keys=2)
        eq(len(l), 2)
        eq(l.is_truncated, True)
        names = [e.name for e in l]
        eq(names, ['bar', 'baz'])

        l = self.bucket.get_all_keys(max_keys=2, marker=names[-1])
        eq(len(l), 1)
        eq(l.is_truncated, False)
        names = [e.name for e in l]
        eq(names, ['foo'])

    @triage
    def test_object_list_delimiter_basic(self):
        """
        operation: list under delimiter
        assertion: prefixes in multi-component object names
        """
        self._create_keys(keys=['foo/bar', 'foo/baz/xyzzy',
                                'quux/thud', 'asdf'])

        # listings should treat / delimiter in a directory-like fashion
        li = self.bucket.list(delimiter='/')
        eq(li.delimiter, '/')

        # asdf is the only terminal object that should appear in the listing
        (keys, prefixes) = _get_keys_prefixes(li)
        names = [e.name for e in keys]
        eq(names, ['asdf'])

        # In Amazon, you will have two CommonPrefixes elements, each with a
        # single prefix. According to Amazon documentation (http://docs.
        # amazonwebservices.com/AmazonS3/latest/API/RESTBucketGET.html),
        # the response's CommonPrefixes should contain all the prefixes,
        # which DHO does.
        #
        # Unfortunately, boto considers a CommonPrefixes element as a prefix,
        # and will store the last Prefix element within a CommonPrefixes
        # element, effectively overwriting any other prefixes.

        # the other returned values should be the pure prefixes foo/ and quux/
        prefix_names = [e.name for e in prefixes]
        eq(len(prefixes), 2)
        eq(prefix_names, ['foo/', 'quux/'])

    @triage
    def test_object_list_delimiter_alt(self):
        """
        operation: list under delimiter
        assertion: non-slash delimiter characters
        """
        self._create_keys(keys=['bar', 'baz', 'cab', 'foo'])

        li = self.bucket.list(delimiter='a')
        eq(li.delimiter, 'a')

        # foo contains no 'a' and so is a complete key
        (keys, prefixes) = _get_keys_prefixes(li)
        names = [e.name for e in keys]
        eq(names, ['foo'])

        # bar, baz, and cab should be broken up by the 'a' delimiters
        prefix_names = [e.name for e in prefixes]
        eq(len(prefixes), 2)
        eq(prefix_names, ['ba', 'ca'])

    @triage
    def test_object_list_delimiter_invalid(self):
        """
        operation: list under delimiter
        assertion: non-printable, empty, unused delimiter can be specified
        """
        key_names = ['bar', 'baz', 'cab', 'foo']
        self._create_keys(keys=key_names)

        for _delimiter in ['\x0a', '', '/']:
            li = self.bucket.list(delimiter=_delimiter)
            eq(li.delimiter, '\x0a')

            (keys, prefixes) = _get_keys_prefixes(li)
            names = [e.name for e in keys]
            eq(names, key_names)
            eq(prefixes, [])

    @triage
    def test_object_list_delimiter_none(self):
        """
        operation: list under delimiter
        assertion: unspecified delimiter defaults to none
        """
        key_names = ['bar', 'baz', 'cab', 'foo']
        self._create_keys(keys=key_names)

        li = self.bucket.list()
        eq(li.delimiter, '')

        (keys, prefixes) = _get_keys_prefixes(li)
        names = [e.name for e in keys]
        eq(names, key_names)
        eq(prefixes, [])

    @triage
    # ecs NextMarker issue: the response NextMarker is not consistent with
    #   aws-s3 that's NextMarker is the last element of Keys.
    @not_supported('fakes3', 'ecs')
    # fakes3 MaxKeys issue, ecs marker issue, ecs NextMarker issue
    def test_object_list_delimiter_prefix(self):
        """
        operation: list under delimiter
        assertion: prefixes in multi-component object names
        """
        self._create_keys(keys=['asdf', 'boo/bar', 'boo/baz/xyzzy',
                                'cquux/thud', 'cquux/bla'])

        bucket = self.bucket
        delim = '/'
        marker = ''
        prefix = ''

        marker = validate_object_list(bucket, prefix, delim, '', 1, True,
                                      ['asdf'], [], 'asdf')
        marker = validate_object_list(bucket, prefix, delim, marker, 1, True,
                                      [], ['boo/'], 'boo/')
        marker = validate_object_list(bucket, prefix, delim, marker, 1, False,
                                      [], ['cquux/'], None)

        marker = validate_object_list(bucket, prefix, delim, '', 2, True,
                                      ['asdf'], ['boo/'], 'boo/')
        marker = validate_object_list(bucket, prefix, delim, marker, 2, False,
                                      [], ['cquux/'], None)

        prefix = 'boo/'

        marker = validate_object_list(bucket, prefix, delim, '', 1, True,
                                      ['boo/bar'], [], 'boo/bar')
        marker = validate_object_list(bucket, prefix, delim, marker, 1, False,
                                      [], ['boo/baz/'], None)

        marker = validate_object_list(bucket, prefix, delim, '', 2, False,
                                      ['boo/bar'], ['boo/baz/'], None)

    @triage
    def test_object_list_return_data(self):
        key_names = ['bar', 'baz', 'foo']
        self._create_keys(keys=key_names)

        # grab the data from each key individually
        data = {}
        for key_name in key_names:
            key = self.bucket.get_key(key_name)
            acl = key.get_acl()
            data.update({
                key_name: {
                    'user_id': acl.owner.id,
                    'display_name': acl.owner.display_name,
                    'etag': key.etag,
                    'last_modified': key.last_modified,
                    'size': key.size,
                    'md5': key.md5,
                    'content_encoding': key.content_encoding,
                    }
                })

        # now grab the data from each key through list
        li = self.bucket.list()
        for key in li:
            key_data = data[key.name]
            eq(key.content_encoding, key_data['content_encoding'])
            eq(key.owner.display_name, key_data['display_name'])
            eq(key.etag, key_data['etag'])
            eq(key.md5, key_data['md5'])
            eq(key.size, key_data['size'])
            eq(key.owner.id, key_data['user_id'])
            _compare_dates(key.last_modified, key_data['last_modified'])

    @triage
    def test_object_list_object_time(self):
        self._create_keys(keys=['foo'])

        key = self.bucket.get_key('foo')
        http_datetime = key.last_modified

        # ISO-6801 formatted datetime
        # there should be only one element, but list doesn't have a __getitem__
        # only an __iter__
        for key in self.bucket.list():
            iso_datetime = key.last_modified

        _compare_dates(iso_datetime, http_datetime)

    def _create_objects(self, num_objects, virtual_folder='', conn=None):
        """
        Create objects with virtual folder
        """
        if conn is None:
            conn = self.data_conn
        for x in range(num_objects):
            key_name = virtual_folder + keyname.get_unique_key_name()
            Key(conn.get_bucket(self.bucket_name), key_name).\
                set_contents_from_string(key_name)
            logger.debug("Create object: %s", key_name)
            self.lock.acquire()
            self.key_list.append(key_name)
            self.lock.release()

    def _assert_object_list(self, marker=None, max_keys=None):
        """
        Do assertion when list object with positive max_keys
        """
        returned_keys = []
        if max_keys is None:
            returned_keys = [key.name for key in self.bucket.get_all_keys()]
        else:
            count = 0
            while count < (constants.LARGE_KEY_NUMBER - 1) / max_keys + 1:
                result_list = [key.name for key in self.bucket.get_all_keys(
                    marker=marker, max_keys=max_keys)]

                # Marker itself should not be a member of object list
                self.assertNotIn(marker, result_list)

                marker = result_list[-1]
                count += 1
                returned_keys.extend(result_list)

        self.assertEqual(set(self.key_list), set(returned_keys))

    def _assert_object_list_negative(self, max_keys):
        """
        Do assertion when list object with negative max_keys
        """
        # It will not raise exception when test on AWS S3
        # no matter what marker is.
        # It will raise S3ResponseError when test on AWS S3
        # if max_keys is negative numbers or not int.
        # It will not raise exception when test on AWS S3
        # if max_keys is 0, but only return empty ResultSet.
        if max_keys == 0:
            self.assertEqual(0, len(self.bucket.get_all_keys(
                max_keys=max_keys)))
        else:
            self.assertRaises(S3ResponseError, lambda max_keys: self.bucket.
                              get_all_keys(max_keys=max_keys), max_keys)

    @triage
    def test_list_empty_bucket(self):
        """ECSTEST-142
        List object within an empty bucket
        """
        self._assert_object_list()

    @triage
    @not_supported('fakes3')
    def test_list_object(self):
        """ECSTEST-140
        List objects within a bucket
        """
        self._create_objects(constants.DEFAULT_KEY_NUMBER)
        self._assert_object_list()

    @known_issue('ecs', 'gouda')
    # Failed on fakes3 if max_keys is not 1000.
    @not_supported('fakes3')
    def test_list_object_with_marker(self):
        """ECSTEST-141
        Create 10k objects
        List the objects with marker:
            Initialize the mark as ''
            Request for at most max_keys objects
            Use the last object key as the marker
                As per S3, marker itself should NOT be a member of object list
            Repeat the request until no object
        Verify all created objects appear during the list
        """
        self._create_objects(constants.MAX_LIST_KEY_NUMBER + 1)

        self._assert_object_list(marker='',
                                 max_keys=constants.MAX_LIST_KEY_NUMBER)
        self._assert_object_list(marker='',
                                 max_keys=constants.MIN_LIST_KEY_NUMBER)
        self._assert_object_list(marker='',
                                 max_keys=constants.DEFAULT_KEY_NUMBER)

    @known_issue('ecs', 'gouda')
    # It will not raise exception when test on fakes3
    #   no matter what marker and max_keys are.
    @not_supported('fakes3')
    def test_list_object_negative(self):
        """ECSTEST-141
        """
        self._create_objects(constants.DEFAULT_KEY_NUMBER)

        self._assert_object_list_negative(0)
        self._assert_object_list_negative(-1)
        self._assert_object_list_negative(1.1)
        self._assert_object_list_negative('str')
        self._assert_object_list_negative(list())
        self._assert_object_list_negative(set())
        self._assert_object_list_negative(tuple())
        self._assert_object_list_negative(dict())

    @triage
    def test_virtual_folder(self):
        """ECSTEST-129
        Test bunch of objects with keys to form a virtual folder like
        structure. List objects with prefix and delimiter to simulate
        'ls' operation.
        """
        virtual_folder = str(uuid.uuid4()) + '/'
        virtual_folder_alt = virtual_folder + str(uuid.uuid4()) + '/'
        result_list = [virtual_folder_alt]
        self._create_objects(constants.DEFAULT_KEY_NUMBER, virtual_folder)
        result_list.extend(self.key_list)
        self._create_objects(constants.DEFAULT_KEY_NUMBER, virtual_folder_alt)
        returned_keys = [key.name for key in self.bucket.get_all_keys(
            prefix=virtual_folder, delimiter='/')]

        self.assertEqual(set(result_list), set(returned_keys))

    @triage
    def test_recursive_virtual_folders(self):
        """ECSTEST-219
        Create several levels, then list them one by one.
        """
        virtual_folder_list = []
        virtual_key_list = []
        for i in range(constants.DEFAULT_VIRTUAL_FOLDER_LEVELS):
            if i == 0:
                virtual_folder_list.append(str(uuid.uuid4()) + '/')
            else:
                virtual_folder_list.append(virtual_folder_list[i-1] +
                                           str(uuid.uuid4()) + '/')
            self._create_objects(constants.DEFAULT_KEY_NUMBER,
                                 virtual_folder_list[i])
            virtual_key_list.append(set(self.key_list))

        for i in range(constants.DEFAULT_VIRTUAL_FOLDER_LEVELS):
            if i == 0:
                virtual_set = virtual_key_list[i]
                virtual_set.add(virtual_folder_list[i+1])
                returned_keys = [key.name for key in self.bucket.get_all_keys(
                    prefix=virtual_folder_list[i], delimiter='/')]
                self.assertEqual(virtual_set, set(returned_keys))

            elif i == constants.DEFAULT_VIRTUAL_FOLDER_LEVELS - 1:
                virtual_set = virtual_key_list[i] - virtual_key_list[i-1]
                returned_keys = [key.name for key in self.bucket.get_all_keys(
                    prefix=virtual_folder_list[i], delimiter='/')]
                self.assertEqual(virtual_set, set(returned_keys))

            else:
                virtual_set = virtual_key_list[i] - virtual_key_list[i-1]
                virtual_set.add(virtual_folder_list[i+1])
                returned_keys = [key.name for key in self.bucket.get_all_keys(
                    prefix=virtual_folder_list[i], delimiter='/')]
                self.assertEqual(virtual_set, set(returned_keys))

    @triage
    def test_virtual_folder_parallel_connection(self):
        """ECSTEST-210
        Create objects from one connection, list them from another connection
        """
        virtual_folder = str(uuid.uuid4()) + '/'
        sub_virtual_folder = virtual_folder + str(uuid.uuid4()) + '/'
        result_list = [sub_virtual_folder]
        self._create_objects(constants.DEFAULT_KEY_NUMBER, virtual_folder)
        result_list.extend(self.key_list)
        self._create_objects(constants.DEFAULT_KEY_NUMBER, sub_virtual_folder)
        bucket = self.alt_data_conn.get_bucket(self.bucket_name)
        returned_keys = [key.name for key in bucket.get_all_keys(
            prefix=virtual_folder, delimiter='/')]

        self.assertEqual(set(result_list), set(returned_keys))

    def _delete_virtual_folder(self, conn, virtual_folder):
        """Delete objects prefixed with virtual_folder
        """
        bucket = conn.get_bucket(self.bucket_name)
        for key in bucket.get_all_keys(prefix=virtual_folder):
            key.delete()

    @triage
    def test_virtual_folder_parallelly_create(self):
        """ECSTEST-210
        Create objects parallelly, list them
        """
        virtual_folder = str(uuid.uuid4()) + '/'
        sub_virtual_folder1 = virtual_folder + str(uuid.uuid4()) + '/'
        sub_virtual_folder2 = virtual_folder + str(uuid.uuid4()) + '/'
        th1 = threading.Thread(target=self._create_objects, args=(
            constants.DEFAULT_KEY_NUMBER, virtual_folder))
        th2 = threading.Thread(target=self._create_objects, args=(
            constants.DEFAULT_KEY_NUMBER, virtual_folder, self.alt_data_conn))
        th3 = threading.Thread(target=self._create_objects, args=(
            constants.DEFAULT_KEY_NUMBER, sub_virtual_folder1))
        th4 = threading.Thread(target=self._create_objects, args=(
            constants.DEFAULT_KEY_NUMBER, sub_virtual_folder2))
        threads = [th1, th2, th3, th4]
        for th in threads:
            th.start()
        for th in threads:
            th.join()
        result_list = [sub_virtual_folder1, sub_virtual_folder2]
        for key in self.key_list:
            if re.match("^%s" % (sub_virtual_folder1), key) is None:
                if re.match("^%s" % (sub_virtual_folder2), key) is None:
                    result_list.append(key)
        returned_keys = [key.name for key in self.bucket.get_all_keys(
            prefix=virtual_folder, delimiter='/')]

        self.assertEqual(set(result_list), set(returned_keys))

    @triage
    def test_virtual_folder_parallel_operation(self):
        """ECSTEST-210
        Create and delete objects parallelly, list them
        """
        virtual_folder = str(uuid.uuid4()) + '/'
        sub_virtual_folder1 = virtual_folder + str(uuid.uuid4()) + '/'
        sub_virtual_folder2 = virtual_folder + str(uuid.uuid4()) + '/'
        self._create_objects(constants.DEFAULT_KEY_NUMBER, virtual_folder)
        result_set = set(self.key_list)
        self._create_objects(constants.DEFAULT_KEY_NUMBER, sub_virtual_folder1)
        th1 = threading.Thread(target=self._create_objects, args=(
            constants.DEFAULT_KEY_NUMBER, sub_virtual_folder2))
        th2 = threading.Thread(target=self._delete_virtual_folder,
                               args=(self.alt_data_conn, sub_virtual_folder1))
        threads = [th1, th2]
        for th in threads:
            th.start()
        for th in threads:
            th.join()
        result_set.add(sub_virtual_folder2)
        returned_keys = [key.name for key in self.bucket.get_all_keys(
            prefix=virtual_folder, delimiter='/')]

        self.assertEqual(result_set, set(returned_keys))

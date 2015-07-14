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

"""Constants used throughout the test suite."""

# test type
TYPE_COMPATIBILITY = 'compatibility'
TYPE_REGRESSION = 'regression'
TYPE_ACCEPTANCE = 'acceptance'
VALID_TYPES = (TYPE_COMPATIBILITY, TYPE_REGRESSION, TYPE_ACCEPTANCE)

# test target type
TARGET_AWSS3 = 'AWSS3'
TARGET_FAKES3 = 'FAKES3'
TARGET_GOUDA = 'GOUDA'
TARGET_BEATLE = 'BEATLE'
TARGET_ECS = 'ECS'
VALID_TARGETS = (TARGET_ECS, TARGET_AWSS3, TARGET_FAKES3, TARGET_GOUDA, TARGET_BEATLE)

# http requests
APPLICATION_JSON = 'application/json'
AUTH_TOKEN_HEADER = 'x-sds-auth-token'
CONTENT_LENGTH = 'Content-Length'
DATE = 'Date'
LAST_MODIFIED = 'Last-Modified'
ETAG = 'Etag'
CONTENT_MD5 = 'Content-MD5'
ALLOWED_TIME_DRIFT = 900  # Most servers allow +/-15 minutes time drift between client and server time
CONTENT_TYPE = 'Content-Type'
AUTHORIZATION = 'Authorization'
TRANSFER_ENCODING = 'Transfer-Encoding'

# unit: byte
ECS_MIN_OBJ_SIZE = 1
ECS_1KB_OBJ_SIZE = 1024
ECS_100KB_OBJ_SIZE = 100 * 1024
ECS_1MB_OBJ_SIZE = 1024 * 1024
ECS_6MB_OBJ_SIZE = 6 * 1024 * 1024
ECS_40MB_OBJ_SIZE = 40 * 1024 * 1024
ECS_1GB_OBJ_SIZE = 1024 * 1024 * 1024
ECS_1GB_PLUS_OBJ_SIZE = ECS_1GB_OBJ_SIZE + 12345 # add a bit salt here
ECS_10GB_PLUS_OBJ_SIZE = ECS_1GB_OBJ_SIZE * 10 + 54321 # add a bit salt here

ECS_10KB_KEY_RANGE = 10 * 1024
ECS_VALID_MIDDLE_OFFSET_OF_KEY = 30 * 1024
ECS_VALID_TAIL_OFFSET_OF_KEY = 90 * 1024
ECS_NEGATIVE_OFFSET_OF_KEY = -20 * 1024

# Bucket list limit by each pagination
ECS_BUCKET_LIST_LIMIT = 1000
# Bucket to create
ECS_LARGE_BUCKET_NUMBER = 3000
# Only list how many pages by pagination
DEFAULT_BUCKET_LIST_PAGES = 3

ECS_BUCKET_THRESHOLD_PER_USER = 5000

DEFAULT_REPEAT_TIMES = 10
LOW_REPEAT_TIMES = 3
MIN_REPEAT_TIMES = 1

DEFAULT_BUCKET_NUMBER = 20
MAX_BUCKET_NUMBER = 99

DEFAULT_SLEEP_SECONDS = 5

DEFAULT_KEY_NUMBER = 20
MAX_DELETE_KEY_NUMBER = 1000
LARGE_KEY_NUMBER = 10000
MAX_LIST_KEY_NUMBER = 1000
MIN_LIST_KEY_NUMBER = 1

SHORTEST_DNS_BUCKET_NAME_LENGTH = 3
LONGEST_DNS_BUCKET_NAME_LENGTH = 63
SHORTEST_EXPAND_BUCKET_NAME_LENGTH = 3
LONGEST_EXPAND_BUCKET_NAME_LENGTH = 255
SHORTEST_ECS_BUCKET_NAME_LENGTH = 1
LONGEST_ECS_BUCKET_NAME_LENGTH = 255

DEFAULT_THREAD_NUMBER = 5

DEFAULT_VIRTUAL_FOLDER_LEVELS = 10
S3_MIN_PART_SIZE = 5 * 1024 * 1024

DEFAULT_LIST_MULTIPART_UPLOAD = 10
MAX_LIST_MULTIPART_UPLOAD = 1000
DEFAULT_LIST_PART_NUMBER = 10
MAX_LIST_PART_NUMBER = 1000

MAX_BUCKET_TAG_KEY_LENGTH = 128
MAX_BUCKET_TAG_VALUE_LENGTH = 256

# Bucket Lifecycle Config
DAYS = 'Days'
RULE_ID = 'ID'
PREFIX = 'Prefix'
STATUS = 'Status'
NONCURRENTDAYS = 'NoncurrentDays'
DATE = 'Date'
MAX_NUM_RULES = 1000
GMT_FORMAT = '%a, %d %b %Y 00:00:00 GMT'

MAX_BUCKET_TAGS_NUMBER = 10

# If '\' was deleted, the response code would be 400,
# rule template must be a line of string
RULE_TEMPLATE_CURRENT_DAYS = """<Rule>\
<ID>%s</ID>\
<Prefix>%s</Prefix>\
<Status>%s</Status>\
<Expiration>\
<Days>%d</Days>\
</Expiration>\
</Rule>"""

RULE_TEMPLATE_CURRENT_DATE = """<Rule>\
<ID>%s</ID>\
<Prefix>%s</Prefix>\
<Status>%s</Status>\
<Expiration>\
<Date>%s</Date>\
</Expiration>\
</Rule>"""

RULE_TEMPLATE_NONCURRENT = """<Rule>\
<ID>%s</ID>\
<Prefix>%s</Prefix>\
<Status>%s</Status>\
<NoncurrentVersionExpiration>\
<NoncurrentDays>%d</NoncurrentDays>\
</NoncurrentVersionExpiration>\
</Rule>"""

SUCCESS = 0
FAILURE = 1

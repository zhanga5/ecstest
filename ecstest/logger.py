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

import os, sys, logging
from ecstest import config

cfg = config.get_config()

def getLogger():
    '''Get a standard logger for testing'''

    formatter = "%(asctime)s %(filename)s:%(lineno)d:%(levelname)s:%(message)s"

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(formatter))
    log_level = logging.INFO
    verbose = cfg['VERBOSE_OUTPUT']
    if verbose:
        log_level = logging.DEBUG
    console_handler.setLevel(log_level)

    logger = logging.getLogger("ecstest_logger")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    return logger

logger = getLogger()


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

import re

from ecstest.constants import (
    TYPE_REGRESSION, TYPE_ACCEPTANCE, TARGET_AWSS3, TARGET_FAKES3
)
from unittest import skip

from ecstest import config


cfg = config.get_config()


def triage(f):
    test_type = cfg['TEST_TYPE']
    relevant_platform = _is_relevant_platform([], triage=True)
    restricted_test_type = test_type in (TYPE_ACCEPTANCE, TYPE_REGRESSION)

    if relevant_platform and restricted_test_type:
        f = skip("Not Yet Triaged")(f)

    f.__ecstest_triage__ = True
    return f


def not_supported(*platforms):

    def not_supported_decorator(f):
        restricted_test_type = False
        test_type = cfg['TEST_TYPE']
        relevant_platform = _is_relevant_platform(platforms)

        if test_type in (TYPE_ACCEPTANCE, TYPE_REGRESSION):
            restricted_test_type = True

        if relevant_platform and restricted_test_type:
            f = skip("Not Supported")(f)
        return f

    return not_supported_decorator


def known_issue(*platforms):

    def known_issue_decorator(f):
        test_type = cfg['TEST_TYPE']
        relevant_platform = _is_relevant_platform(platforms)
        restricted_test_type = True if test_type == TYPE_REGRESSION else False
        if relevant_platform and restricted_test_type:
            f = skip("Known Issue")(f)
        return f

    return known_issue_decorator


def disabled(f):
    run_disabled = cfg['RUN_DISABLED']

    if not run_disabled:
        f = skip("Disabled")(f)

    return f


def _is_relevant_platform(platforms, triage=False):
    relevant_platform = False
    test_targets = re.split('\s*,\s*', cfg['TEST_TARGET'])

    if not triage:
        for test_target in [x.lower() for x in test_targets]:
            if test_target in platforms:
                relevant_platform = True
                break

    else:
        for test_target in test_targets:
            if test_target not in (TARGET_AWSS3, TARGET_FAKES3):
                relevant_platform = True
                break

    return relevant_platform

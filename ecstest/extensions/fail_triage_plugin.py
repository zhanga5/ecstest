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

import logging
import os
from unittest.case import _ExpectedFailure

from nose.plugins import Plugin

log = logging.getLogger('ecstest.extensions.fail_triage_plugin')


class FailTriagePlugin(Plugin):
    name = 'fail-triage'

    def options(self, parser, env=os.environ):
        super(FailTriagePlugin, self).options(parser, env=env)

    def configure(self, options, conf):
        super(FailTriagePlugin, self).configure(options, conf)
        # if not self.enabled:
        #     return

    def wantMethod(self, method):
        # Select only tests that have the @triage decorator
        return getattr(method, "__ecstest_triage__", False)

    def prepareTestCase(self, test):
        # ensure all tests selected fail
        def fail_run(result):
            # We need to make these plugin calls because there won't be
            # a result proxy, due to using a stripped-down test suite
            self.conf.plugins.startTest(test)
            result.startTest(test)
            self.conf.plugins.addSuccess(test)
            exception = AssertionError("Failed due to fail-triage plugin")
            result.addFailure(test, (_ExpectedFailure, exception, None))
            self.conf.plugins.stopTest(test)
            result.stopTest(test)

        return fail_run

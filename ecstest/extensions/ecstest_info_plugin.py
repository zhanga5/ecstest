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
import re

from nose.plugins import Plugin

log = logging.getLogger('ecstest.extensions.ecstest_info_plugin')


class InfoPlugin(Plugin):
    name = 'ecstest-info'

    def options(self, parser, env=os.environ):
        super(InfoPlugin, self).options(parser, env=env)

    def configure(self, options, conf):
        super(InfoPlugin, self).configure(options, conf)
        if not self.enabled:
            return

    def describeTest(self, test):
        method_name = test.test._testMethodName
        docstring = test.test._testMethodDoc or ""
        match = re.search(r"(ECSTEST\-\d+)", docstring)
        jira_id = " ({})".format(match.group(0)) if match else ""
        return "{}{}".format(method_name, jira_id)

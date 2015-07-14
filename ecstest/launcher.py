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

import nose.core
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description='Run ECSTEST Test Suite against something vaguely s3 compatible.')
    parser.add_argument('--module', dest="module", action='store', default=None,
                        help="submodule of ecstest.testcases to run:  'dataplane' or 'controlplane' for now")
    parser.add_argument('--dns-override', dest="dns_override", action='append', default=[],
                        help="override DNS while running tests: mask:ip (multiple times is ok)")

    (args, other_args) = parser.parse_known_args()
    module = 'ecstest.testcases'
    if args.module:
        module = 'ecstest.testcases.{}'.format(args.module)
    if args.dns_override:
        import etchosts

        for line in args.dns_override:
            mask, ip = line.split(':')

            etchosts.add(mask, ip)

    # remove args we've already parsed from sys.argv so that nose doesn't attempt to reprocess
    sys.argv = [sys.argv[0]]
    sys.argv.extend(other_args)

    nose.core.main(defaultTest=module)

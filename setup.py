#!/usr/bin/env python
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


from setuptools import setup

# In python < 2.7.4, a lazy loading of package `pbr` will break
# setuptools if some other modules registered functions in `atexit`.
# solution from: http://bugs.python.org/issue15881#msg170215
try:
    import multiprocessing  # noqa
except ImportError:
    pass

setup(
    setup_requires=['pbr'],
    pbr=True,
    entry_points={
        'console_scripts': [
            'ecstest = ecstest.launcher:main'
        ],
        'nose.plugins.0.10': [
            'fail_triage_plugin = ecstest.extensions.fail_triage_plugin:FailTriagePlugin',
            'ecstest_info_plugin = ecstest.extensions.ecstest_info_plugin:InfoPlugin'
        ]
    }
)

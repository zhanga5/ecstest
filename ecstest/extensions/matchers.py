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


"""Define custom testtools matchers for easier API validation.
This allows the TestCase class to be extended to include custom assertion
methods that implement these matchers.

These matchers follow the pattern as laid out in the testtools repo:
https://github.com/testing-cabal/testtools/tree/master/testtools/matchers
"""

import jsonschema
from testtools.compat import text_repr
from testtools.matchers._impl import Matcher, Mismatch


class JsonSchemaMatcher(Matcher):
    """Matcher that compares a json object to a schema."""
    def __init__(self, expected):
        """Instantiate the matcher

        :param expected: the json schema used to validate the given json
        """
        self.expected = expected

    def __str__(self):
        return "%s(%r)" % (self.__class__.__name__, self.expected)

    def match(self, other):
        """Perform the json schema validation Return a JsonSchemaMismatch if
        the json does not match the schema.

        :param other: the json object to be validated against the schema
        """
        try:
            jsonschema.validate(
                instance=other, schema=self.expected,
                cls=jsonschema.Draft4Validator)
            return None
        except jsonschema.ValidationError as val_err:
            # create a meaningful message
            schema_path = [item for item in val_err.schema_path]
            err_msg = "JSON Schema Error: {0}, {1} {2} ".format(
                schema_path, val_err.message, val_err.schema)
            return _JsonSchemaMismatch(other, self.expected, err_msg)


class _JsonSchemaMismatch(Mismatch):

    def __init__(self, json, schema, err_msg):
        """Create a DoesNotStartWith Mismatch.
        :param json: the json object.
        :param schema: the json schema used to perform validation.
        :param err_msg: details of the failed json schema validation
        """
        self.json = json
        self.schema = schema
        self.err_msg = err_msg

    def describe(self):
        return "%s does not comply with schema %s. msg: %s" % (
            text_repr(str(self.json)), text_repr(str(self.schema)),
            text_repr(self.err_msg))

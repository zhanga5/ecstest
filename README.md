# ecstest

A functional test suite for testing [EMC ECS](https://www.emc.com/storage/ecs-appliance/index.htm) deployments.

The test suite is based off of the [testtools](http://testtools.readthedocs.org/) library
for creating tests that use [assertions](http://testtools.readthedocs.org/en/latest/for-test-authors.html#assertions).  
The library contains methods for test setup, teardown, and helper libraries for matchers and delayed assertions.

Every test included should make assertions about the feature it is testing, such as return codes,
response bodies, status codes, expected headers, etc.


## Multi-Use Test Suite

The ecstest suite is an s3 compatibility suite that can be run against multiple backends or targets.
Current supported targets are:
- `awss3` execute against Amazon S3 service
- `fakes3`execute against fake63 service for local development
- `ecs` execute against EMC ECS
- `gouda` execute against ECR data plane proxy running against ECS
- `silenus`execute agianst Silenus control plane proxy

The test suite serve multiple purposes for each target:
- Test s3 compatibility of the product
- Act as a regression test suite to gate new changes to the products
- Track known issues/bugs in each product that are identified by failing tests

**Test Suite Requirements:**
- New tests added should not interfere with existing regression tests.
- Individual test need to be categorized into 3 main categories for **RegressionTest**, **Known Issue**, and **Not Supported**
- Tests need to be able to be in different categories based on the execution target of the test suite(ECR, ECS, Silenus)


## Using Decorators to Manage Categorization of Tests, and Test Runs

By default, tests without a decorator applied will be considered Regression tests.
This ensures that by default a test will gate the release of code for the target system.

**Categorization decorators:**
- `@triage` - The triage decorator should be used on all new tests that are added to the test suite.  
This will mark tests that need to be triaged as well as prevent these tests from being run in the regression test suite
- `@known_issue('<target>', '<target>')` - a failing test that has been identified as an incompatibility or bug that will be fixed at a later date.  Accepts arguments specifying which targets it applies to.
- `@not_supported('<target>', '<target>')` - a failing test for an incompatibility that will not be supported or fixed.  Accepts arguments specifying which targets it applies to.


**Examples:**

```python

class TestDecoratorExample(testbase.EcsDataPlaneTestBase):
    
    @triage
    def test_triage(self):
        """This decorator identifies this as a new tests that 
        needs to be triaged/categorized.
        """
        pass
    
    @known_issue('gouda', 'ecs')
    def test_known_issue(self):
        """This decorator marks this test as a know issue for ECR and ECS
        """
        pass
        
    @known_issue('ecs')
    @not_supported('gouda', 'fakes3')
    def test_multiple_categorization(self):
        """This test is marked as a known bug for ECS, but is marked as 
        feature that is not supported for ECR or FAKES3.
        """
        pass
        
    @not_supported('gouda', 'ecs')
    def test_multiple_categorization(self):
        """This test is marked as a feature that 
        is not supported for ECR or ECS.
        """
        pass
```

## Manage Test Runs by Type

There should be multiple types of test runs that have different behavior:
- `TYPE_COMPATIBILITY` execute all tests in the test suite regardless of categorization, as it measures overall s3 compatibility.
- `TYPE_REGRESSION` execute all tests that are not marked with a categorization decorator.
- `TYPE_ACCEPTANCE` execute all regression tests + all tests marked with @known_issue.  This is to test all functionality that should be supported.
- `TYPE_TRIAGE` execute only @triage tests so that results may be used to further categorize tests.
- `TYPE_EXPECTED_FAILURES` execute all @known_issue tests as expected failures to determine if any bugs have been fixed.

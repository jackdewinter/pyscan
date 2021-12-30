# Project Summarizer

[![GitHub top language](https://img.shields.io/github/languages/top/jackdewinter/pyscan)](https://github.com/jackdewinter/pyscan)
![platforms](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey)
[![Python Versions](https://img.shields.io/pypi/pyversions/project_summarizer.svg)](https://pypi.org/project/project_summarizer)
[![Version](https://img.shields.io/pypi/v/project_summarizer.svg)](https://pypi.org/project/project_summarizer)

[![GitHub Workflow Status (event)](https://img.shields.io/github/workflow/status/jackdewinter/pyscan/Main)](https://github.com/jackdewinter/pyscan/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/jackdewinter/pymarkdown/branch/main/graph/badge.svg?token=PD5TKS8NQQ)](https://codecov.io/gh/jackdewinter/pyscan)
![GitHub Pipenv locked dependency version (branch)](https://img.shields.io/github/pipenv/locked/dependency-version/jackdewinter/pyscan/black/master)
![GitHub Pipenv locked dependency version (branch)](https://img.shields.io/github/pipenv/locked/dependency-version/jackdewinter/pyscan/flake8/master)
![GitHub Pipenv locked dependency version (branch)](https://img.shields.io/github/pipenv/locked/dependency-version/jackdewinter/pyscan/pylint/master)
[![Sourcery](https://img.shields.io/badge/Sourcery-enabled-brightgreen)](https://sourcery.ai)
[![Stars](https://img.shields.io/github/stars/jackdewinter/pyscan.svg)](https://github.com/jackdewinter/pyscan/stargazers)
[![Downloads](https://img.shields.io/pypi/dm/project_summarizer.svg)](https://pypistats.org/packages/project_summarizer)

[![Issues](https://img.shields.io/github/issues/jackdewinter/pyscan.svg)](https://github.com/jackdewinter/pyscan/issues)
[![License](https://img.shields.io/github/license/jackdewinter/pyscan.svg)](https://github.com/jackdewinter/pyscan/blob/main/LICENSE.txt)
[![Contributors](https://img.shields.io/github/contributors/jackdewinter/pyscan.svg)](https://github.com/jackdewinter/pyscan/graphs/contributors)
[![Forks](https://img.shields.io/github/forks/jackdewinter/pyscan.svg)](https://github.com/jackdewinter/pyscan/network/members)

[![LinkedIn](https://img.shields.io/badge/-LinkedIn-black.svg?logo=linkedin&colorB=555)](https://www.linkedin.com/in/jackdewinter/)

## TL;DR

Project Summarizer is a tool used to summarize various files produced by other tools during a build or test process.
This tool is intended to be executed after running a test script or a build script.
The benefit to using the Project Summarizer tool is a quick summary of more terse information provided by other tools.
The goal is to provide the minimum level of feedback on changes to the project, avoiding a more costly lookup of the summarized information.
If that goal is met, then a simple look at that summarized information can replace a more costly lookup, such as having to switch focus to a locally hosted web page to determine impact.

Our hope is that we can help developers achieve that goal at least 50 percent of the time.

## Supported Summarizers

The currently supported summarizers are:

- [JUnit](https://junit.org/junit5/) for test results
  - supported by JUnit and [PyTest](https://docs.pytest.org/en/6.2.x/)
- [Cobertura](https://github.com/cobertura/cobertura) for code coverage
  - supported by [pytest-cov](https://pypi.org/project/pytest-cov/)

There are plans for an extension mechanism to support other summarizers soon.

## Getting Started

The *what* is reported on and the *how* that information is generated is up to the developer team for every project.
The Project Summarizer tool aims to condense that reported information into a simple, glanceable report.

Normally a project will have a build/test framework or a build/test script to perform this action.
The Project Summarizer tool can then be added to the end of that process, to be executed on success or failure.
If the project uses a test framework that exports a JUnit compatible results file, then the argument `--junit <file>` is used when calling the Project Summarizer tool.
If the project uses a coverage framework that exports a Cobertura compatible coverage file, then the argument `--cobertura <file>` is used when calling the Project Summarizer tool.

When setup this way, the tool will present a quick summary of the contents of those two files.
In addition, the tool will create summary files in the `report` directory of the project.
While the report files are not intended for human consumption, their summarized information should be easy enough to read and understand, if needed.

## Normal Usage

While complete information on the current state of the project is useful, our development team finds that most often that they are looking for what has changed.
That is where the Project Summarizer tool shines.
But, to understand what has changed, a benchmark or snapshot of the previous "current" state must be placed somewhere.
For the Project Summarizer tool, those summary files in the `report` directory are *published* to the `publish` directory using the `--publish` argument.
In our team, publishing is performed as the last action before committing changes to a project's repository.
The intent of that action is that we can always determine what changes have occurred since the last commit.
If we have any doubts about the integrity of that information, we can publish the summaries at the start of working on a new issue, just to get the confidence that we have the right summaries.

Once the project's summaries have been published, the `--only-changes` argument can then be used to report only on the changes that have occurred since the last published summaries.
With that argument present, the summaries will not only display values that have changed since the published summaries, along with the amount of change that has occurred.
If adding, removing, or enabling tests, this is useful to make sure that the count of changed tests is as expected.
If making any changes to the code that the tests are covering, this is useful to see what effect the change has on code coverage metrics.

Our team uses test driven development and maintains a high code coverage metric for all our projects.
The Project Summarizer tool allows us to see the impact of our current changes on the current existing tests, enabled and disabled.
It also allows us to keep track of the impact of any code changes on our coverage metrics.
With both summaries, if the reported information is outside of our expectations, we can then look at the more comprehensive reports to find that needed information.
But over half of the time, the summary information alone is enough to answer our questions about the changes we have made.

It is recommended that projects do not commit the contents of the `report` directory to a repository, and only commit the contents of the `publish` directory.
While the decision to follow that recommendation is up to development teams, our team has found that it provides a particularly useful summary of what has changed since the last commit.
That information has helped our team ensure that the right tests have changed and that our code coverage is not negatively affected, all with a simple glance.

## Sample Output

These samples were captured against the Project Summarizer project itself and have not been modified.

### Full Output

Generated against [this commit](https://github.com/jackdewinter/pyscan/commit/86daf5d9c5607362e6e70ad3af956da15175ff15).

```text
Test Results Summary
--------------------


  CLASS NAME                    TOTAL TESTS  FAILED TESTS  SKIPPED TESTS

  test.test_coverage_model                6             0              0
  test.test_coverage_profiles             3             0              0
  test.test_coverage_scenarios           12             0              0
  test.test_main                          4             0              0
  test.test_publish_scenarios             9             0              0
  test.test_results_scenarios            19             0              0
  test.test_scenarios                     1             0              0
  ---                                    --             -              -
  TOTALS                                 54             0              0

Test Coverage Summary
---------------------


  TYPE          COVERED  MEASURED  PERCENTAGE

  Instructions      ---       ---      ------
  Lines             563       563      100.00
  Branches          184       184      100.00
  Complexity        ---       ---      ------
  Methods           ---       ---      ------
  Classes           ---       ---      ------
```

### Only Output Changes with No Changes

Generated against [this commit](https://github.com/jackdewinter/pyscan/commit/86daf5d9c5607362e6e70ad3af956da15175ff15) with no observable changes.

```text
Test Results Summary
--------------------

Test results have not changed since last published test results.

Test Coverage Summary
---------------------

Test coverage has not changed since last published test coverage.
```

### Expected Change

Generated against [this commit](https://github.com/jackdewinter/pyscan/commit/86daf5d9c5607362e6e70ad3af956da15175ff15).
Test function `test_junit_jacoco_profile` renamed to `xxtest_junit_jacoco_profile` to not be executed.

```text
Test Results Summary
--------------------


  CLASS NAME                   TOTAL TESTS  FAILED TESTS  SKIPPED TESTS

  test.test_coverage_profiles       2 (-1)             0              0
  ---                              --                  -              -
  TOTALS                           53 (-1)             0              0


Test Coverage Summary
---------------------


  TYPE       COVERED  MEASURED     PERCENTAGE

  Lines     557 (-6)       563  98.93 (-1.07)
  Branches  178 (-6)       184  96.74 (-3.26)
```

## Note

Our team's development is primarily done on Windows systems.
As such, any examples that we present will typically be Windows CMD scripts.
We have a project note to provide Bash scripts for the project soon.

## Using This Project On Itself - Setup

For the Project Summarizer project itself, there is a `ptest.cmd` script that allows for various modes to be used in executing PyTest against the project.
These different modes allow for more focused testing depending on the needs of the developer at the time.
Those different modes use environment variables to specify how to execute PyTest, and for the purpose of this documentation, those variables are ignored to provide a clearer picture of how the Project Summarizer tool works.

With those other environment variables out of the way, the heart of the script is the `PYTEST_ARGS` environment variable.
Under normal operation, that environment variable is set to:

```text
--timeout=10 -ra --strict-markers --junitxml=report/tests.xml --html=report/report.html
```

When testing with code coverage applied, the following text is appended to the contents of that variable:

```text
--cov --cov-branch --cov-report xml:report/coverage.xml --cov-report html:report/coverage
```

As the project uses `pipenv`, when the tests are executed, they are effectively executed with the following command line:

```cmd
pipenv run pytest %PYTEST_ARGS%
```

The important parts here are the `--junitxml` argument and the `--cov-report xml:` argument to PyTest.
The first argument specifies the location where the JUnit compatible report of test results will be written.
Similarly, the second argument specifies the location where the Cobertura compatible report of test coverage will be written.

## Using This Project On Itself - Adding In Project Summarizer

Given that setup, adding in the Project Summarizer to the `ptest.cmd` script is easy.
As code coverage can sometimes slow test execution, the following section of the script is used to setup the execution of the tool:

```cmd
set PTEST_REPORT_OPTIONS=--junit %PTEST_TEST_RESULTS_PATH%
if defined PTEST_COVERAGE_MODE (
    if not defined TEST_EXECUTION_FAILED (
        set PTEST_REPORT_OPTIONS=%PTEST_REPORT_OPTIONS% --cobertura %PTEST_TEST_COVERAGE_PATH%
    )
)
pipenv run %PTEST_PROJECT_SUMMARIZER_SCRIPT_PATH% %PTEST_PROJECT_SUMMARIZER_OPTIONS% %PTEST_REPORT_OPTIONS%
```

As the summarizer is being used in the same project as it is created in, the `PTEST_PROJECT_SUMMARIZER_SCRIPT_PATH` variable is set to point to the project's `main.py` module.
Normally, that value would be the name of the Python package `project_summarizer`.
The `PTEST_PROJECT_SUMMARIZER_OPTIONS` variable contains the `--only-changes` argument by default but can be turned off if desired.
The `PTEST_TEST_RESULTS_PATH` variable is set to `report\tests.xml` to correspond with the `--junitxml=report/tests.xml` argument passed to PyTest.
The `PTEST_TEST_COVERAGE_PATH` variable is set to `report\coverage.xml` to match the `--cov-report xml:report/coverage.xml` argument passed to PyTest.

Because our team wanted publishing summaries to be a function of testing, there is an alternate flow in the `ptest.cmd` script that published the summaries.
This is easy accomplished by invoking the summarizer with only the `--publish` argument.

## Using This Project On Itself - Generating The Above Samples

All the samples in the [Sample Output](#sample-output) section are generated using the `ptest.cmd` script with the Project Summarizer tool added in.

- used as part of the normal development process, `ptest.cmd --publish` was previously invoked to benchmark the summaries for the last commit
  - this effectively invoked `project_summarizer --publish`
- `ptest -c -f` was invoked to run tests with coverage and provide the [Full Output sample](#full-output)
  - this ran PyTest with coverage enabled, and effectively invoked `project_summarizer --junit report\tests.xml --cobertura report\coverage.xml`
- `ptest -c` was invoked to run tests with coverage and present the [No Change sample](#only-output-changes-with-no-changes)
  - this ran PyTest with coverage enabled, and effectively invoked `project_summarizer --only-changes --junit report\tests.xml --cobertura report\coverage.xml`
- `ptest -c` was invoked to run tests with coverage and present the [Expected Change sample](#expected-change)
  - same as above, but with the test "missing", it reported that test as not being executed and reported the coverage that was missing

## Future Goals

The initial 0.5.0 release is to get this project on the board.
Once that is done, we have plans to implement an extension mechanism to provide for customized summaries.

## When Did Things Change?

The changelog for this project is maintained [at this location](/changelog.md).

## Still Have Questions?

If you still have questions, please consult our [Frequently Asked Questions](/docs/faq.md) document.

## Contact Information

If you would like to report an issue with the tool or the documentation, please file an issue [using GitHub](https://github.com/jackdewinter/pyscan/issues).

If you would like to us to implement a feature that you believe is important, please file an issue [using GitHub](https://github.com/jackdewinter/pyscan/issues) that includes what you want to add, why you want to add it, and why it is important.
Please note that the issue will usually be the start of a conversation and be ready for more questions.

If you would like to contribute to the project in a more substantial manner, please contact me at `jack.de.winter` at `outlook.com`.

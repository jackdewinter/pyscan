# Note

Our team is equally versed at using the Windows CMD scripts as we are using Bash
scripts. For convenience, the following examples will refer to the `ptest.sh` Bash
script for executing a series of tests and observing the changes in the summary
information.  Those references to `ptest.sh` can easily be replaced with the
`ptest.cmd` scripts with no issues.

## Using This Project On Itself - Setup

For the Project Summarizer project itself, there is a `ptest.sh` script that allows
for various modes to be used in executing PyTest against the project. These different
modes allow for more focused testing depending on the needs of the developer at
the time. Those different modes use environment variables to specify how to execute
PyTest, and for the purpose of this documentation, those variables are ignored to
supply a clearer picture of how the Project Summarizer tool works.

Focusing explicitly on executing PyTest, either `pytest_args` (Bash) or
`PYTEST_ARGS` (Cmd) are set to:

```text
--timeout=10 -ra --strict-markers --junitxml=report/tests.xml --html=report/report.html
```

When testing with code coverage applied, the following text is appended to the
contents of that variable:

```text
--cov --cov-branch --cov-report xml:report/coverage.xml --cov-report html:report/coverage
```

As the project uses PipEnv, when the tests are executed, they are effectively
executed with the following command line:

```sh
pipenv run pytest ${pytest_args}
```

or

```cmd
pipenv run pytest %PYTEST_ARGS%
```

The important parts here are the `--junitxml` argument and the `--cov-report xml:`
arguments passed to PyTest. The first argument specifies the location where the
JUnit compatible report of test results will be written. The second argument specifies
the location where the Cobertura compatible report of test coverage will be written.

## Using This Project On Itself - Adding In Project Summarizer

Given that setup, adding in the Project Summarizer to the `ptest.sh` script is
easy. As code coverage can sometimes slow test execution, the following function
controls the execution of the tool:

```sh
summarize_test_executions() {

    # Determine if we report on the tests, or tests + coverage.
    PYSCAN_REPORT_OPTIONS=(--junit "${TEST_RESULTS_XML_PATH}")
    if [[ ${COVERAGE_MODE} -ne 0 ]]; then
        if [[ ${TEST_EXECUTION_SUCCEEDED} -ne 0 ]]; then
            PYSCAN_REPORT_OPTIONS+=(--cobertura "${TEST_COVERAGE_XML_PATH}")
        else
            echo "{Coverage was specified, but one or more tests failed.  Skipping reporting of coverage.}"
        fi
    fi

    echo "{Summarizing changes in execution of full test suite.}"
    if ! pipenv run ${PYSCAN_SCRIPT_PATH} ${PYSCAN_OPTIONS} "${PYSCAN_REPORT_OPTIONS[@]}"; then
        echo ""
        complete_process 1 "{Summarizing changes in execution of full test suite failed.}"
    fi
}
```

As the summarizer is being used in the same project as it is created in, the
`PYSCAN_SCRIPT_PATH` variable is set to point to the project's `main.py` module.
Normally, that value would be the name of the Python package `project_summarizer`.
The `PYSCAN_OPTIONS` variable holds the `--only-changes` argument by default but
can be turned off if desired. The `TEST_RESULTS_XML_PATH` variable is set to
`report\tests.xml` to correspond with the `--junitxml=report/tests.xml` argument
passed to PyTest. The `TEST_COVERAGE_XML_PATH` variable is set to `report\coverage.xml`
to match the `--cov-report xml:report/coverage.xml` argument passed to PyTest.

Because our team wanted publishing summaries to be a function of testing, there
is an alternate flow in the `ptest.sh` script that published the summaries.
This is easy accomplished by invoking the summarizer with only the `--publish` argument.

## Using This Project On Itself - Generating The Above Samples

All the samples in the [Sample Output](./getting-started.md#sample-output) section
are generated using the `ptest.sh` script with the Project Summarizer tool added
in.

- used as part of the normal development process, `ptest.sh --publish` was previously
  invoked to benchmark the summaries for the last commit
    - this effectively invoked `project_summarizer --publish`
- `ptest.sh -c -f` was invoked to run tests with coverage and supply the
  [Full Output sample](./getting-started.md#full-output)
    - this ran PyTest with coverage enabled, and effectively invoked
      `project_summarizer --junit report\tests.xml --cobertura report\coverage.xml`
- `ptest.sh -c` was invoked to run tests with coverage and present the
  [No Change sample](./getting-started.md#only-output-changes-with-no-changes)
    - this ran PyTest with coverage enabled, and effectively invoked
      `project_summarizer --only-changes --junit report\tests.xml --cobertura report\coverage.xml`
- `ptest.sh -c` was invoked to run tests with coverage and present the
  [Expected Change sample](./getting-started.md#expected-change)
    - same as above, but with the test "missing", it reported that test as not
      being executed and reported the coverage that was missing

## Advanced Features

### Quiet Mode and Output Character Columns

After use in different real-world scenarios, the ability to maintain better control
on the report output became more apparent. To that extent, two new arguments were
added to the command line: `--quiet` and `--columns`. The `--quiet` argument instructs
the report summarizers to only generate their output files, and not to generate
any console output. This feature is useful on servers where the tool is still executed
to keep things coordinated with developer workflows, but the console output is not
important. In those cases where the output on servers is relevant, the `--columns`
argument is useful in specifying the number of character columns to use for the
output. The integer value passed after the `--columns` argument is passed to the
table formatting package that is suggested for plugins: `columnar`. In the past,
when the tool has been run on server environments, there have been situations where
the `columnar` package's determination of number of output columns has been wrong
or had returned `0`. By using this setting, those situations can be sidestepped
by hardwiring the number of columns from the command line.

### Setting The Reporting and Publishing Directories

As mentioned above, the `report` directory is used to generate summary reports in,
and those reports can then be published into the `publish` directory. If different
names are wanted for these two directories, they can be set with the `--report-dir`
argument and the `--publish-dir` argument. Note that the report directory, either
the default `report` or the value supplied with the `--report-dir` argument, must
exist before this tool is called. However, the publish directory, either the default
`publish` or the value supplied with the `--publish-dir` argument, will be created
if it does not exist.

# Getting Started

The *what* is reported on and the *how* that information is generated is up to
the developer team for every project. The Project Summarizer tool aims to condense
that reported information into a simple, glanceable report.

Normally a project will have a build/test framework or a build/test script to perform
this action. The Project Summarizer tool can then be added to the end of that process,
to be executed on success or failure. If the project uses a test framework that
exports a JUnit compatible results file, then the argument `--junit <file>` is
used when calling the Project Summarizer tool. If the project uses a coverage framework
that exports a Cobertura compatible coverage file, then the argument
`--cobertura <file>` is used when calling the Project Summarizer tool.

When setup this way, the tool will present a quick summary of the contents of those
two files. In addition, the tool will create summary files in the `report` directory
of the project. While the report files are not intended for human consumption, their
summarized information should be easy enough to read and understand, if needed.

## Normal Usage

While complete information on the current state of the project is useful, our
development team finds that most often that they are looking for what has changed.
That is where the Project Summarizer tool shines. But, to understand what has changed,
a benchmark or snapshot of an earlier "current" state must be placed somewhere.
For the Project Summarizer tool, those summary files in the `report` directory
are *published* to the `publish` directory using the `--publish` argument. In our
team, publishing is performed as the last action before committing changes to a
project's repository. The intent of that action is that we can always determine
what changes have occurred since the last commit. If we have any doubts about the
integrity of that information, we can publish the summaries at the start of working
on a new issue, just to get the confidence that we have the right summaries.

Once the project's summaries have been published, the `--only-changes` argument
can then be used to report only on the changes that have occurred since the last
published summaries. With that argument present, the summaries will not only display
values that have changed since the published summaries, along with the amount of
change that has occurred. If adding, removing, or enabling tests, this is useful
to make sure that the count of changed tests is as expected. If making any changes
to the code that the tests are covering, this is useful to see what effect the change
has on code coverage metrics.

Our team uses test driven development and keeps a high code coverage metric for
all our projects. The Project Summarizer tool allows us to see the impact of our
current changes on the current existing tests, enabled and disabled. It also allows
us to keep track of the impact of any code changes on our coverage metrics. With
both summaries, if the reported information is outside of our expectations, we
can then look at the more comprehensive reports to find that needed information.
But over half of the time, the summary information alone is enough to answer our
questions about the changes we have made.

It is recommended that projects do not commit the contents of the `report` directory
to a repository, and only commit the contents of the `publish` directory. While
the decision to follow that recommendation is up to development teams, our team
has found that it provides a particularly useful summary of what has changed since
the last commit. That information has helped our team ensure that the right tests
have changed and that our code coverage is not negatively affected, all with a
simple glance. To enforce this in out projects, we added the following line to
our `.gitignore` files:

```text
report/
```

## Sample Output

These samples were captured against the Project Summarizer project itself and have
not been changed.

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

Generated against [this commit](https://github.com/jackdewinter/pyscan/commit/86daf5d9c5607362e6e70ad3af956da15175ff15)
with no observable changes.

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
Test function `test_junit_jacoco_profile` renamed to `xxtest_junit_jacoco_profile`
to not be executed.

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

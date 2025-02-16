# Project Summarizer

|   |   |
|---|---|
|Project|[![Version](https://img.shields.io/pypi/v/project_summarizer.svg)](https://pypi.org/project/project_summarizer)  [![Python Versions](https://img.shields.io/pypi/pyversions/project_summarizer.svg)](https://pypi.org/project/project_summarizer)  ![platforms](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey)  [![License](https://img.shields.io/github/license/jackdewinter/pyscan.svg)](https://github.com/jackdewinter/pyscan/blob/master/LICENSE.txt)  [![GitHub top language](https://img.shields.io/github/languages/top/jackdewinter/pyscan)](https://github.com/jackdewinter/pyscan)|
|Quality|[![GitHub Workflow Status (event)](https://img.shields.io/github/workflow/status/jackdewinter/pyscan/Main)](https://github.com/jackdewinter/pyscan/actions/workflows/main.yml)  [![Issues](https://img.shields.io/github/issues/jackdewinter/pyscan.svg)](https://github.com/jackdewinter/pyscan/issues)  [![codecov](https://codecov.io/gh/jackdewinter/pymarkdown/branch/main/graph/badge.svg?token=PD5TKS8NQQ)](https://codecov.io/gh/jackdewinter/pyscan)  [![Sourcery](https://img.shields.io/badge/Sourcery-enabled-brightgreen)](https://sourcery.ai)  ![snyk](https://img.shields.io/snyk/vulnerabilities/github/jackdewinter/pyscan) |
|  |![GitHub Pipenv locked dependency version (branch)](https://img.shields.io/github/pipenv/locked/dependency-version/jackdewinter/pyscan/black/master)  ![GitHub Pipenv locked dependency version (branch)](https://img.shields.io/github/pipenv/locked/dependency-version/jackdewinter/pyscan/flake8/master)  ![GitHub Pipenv locked dependency version (branch)](https://img.shields.io/github/pipenv/locked/dependency-version/jackdewinter/pyscan/pylint/master)  ![GitHub Pipenv locked dependency version (branch)](https://img.shields.io/github/pipenv/locked/dependency-version/jackdewinter/pyscan/mypy/master)  ![GitHub Pipenv locked dependency version (branch)](https://img.shields.io/github/pipenv/locked/dependency-version/jackdewinter/pyscan/pyroma/master)  ![GitHub Pipenv locked dependency version (branch)](https://img.shields.io/github/pipenv/locked/dependency-version/jackdewinter/pyscan/pre-commit/master)|
|Community|[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/jackdewinter/pyscan/graphs/commit-activity) [![Stars](https://img.shields.io/github/stars/jackdewinter/pyscan.svg)](https://github.com/jackdewinter/pyscan/stargazers)  [![Forks](https://img.shields.io/github/forks/jackdewinter/pyscan.svg)](https://github.com/jackdewinter/pyscan/network/members)  [![Contributors](https://img.shields.io/github/contributors/jackdewinter/pyscan.svg)](https://github.com/jackdewinter/pyscan/graphs/contributors)  [![Downloads](https://img.shields.io/pypi/dm/project_summarizer.svg)](https://pypistats.org/packages/project_summarizer)|
|Maintainers|[![LinkedIn](https://img.shields.io/badge/-LinkedIn-black.svg?logo=linkedin&colorB=555)](https://www.linkedin.com/in/jackdewinter/)|

## TL;DR

Project Summarizer is a tool used to summarize various files produced by other tools during a build or test process.
This tool is intended to be executed after running a test script or a build script.
The benefit to using the Project Summarizer tool is a quick summary of more terse information provided by other tools.
The goal is to provide the minimum level of feedback on changes to the project, avoiding a more costly lookup of the summarized information.
If that goal is met, then a simple look at that summarized information can replace a more costly lookup, such as having to switch focus to a locally hosted web page to figure out the impact of a change.

Our hope is that we can help developers achieve that goal at least 50 percent of the time.

## Supported Summarizers

The currently supported summarizers are:

- [JUnit](https://junit.org/junit5/) for test results
  - supported by JUnit and [PyTest](https://docs.pytest.org/en/6.2.x/)
- [Cobertura](https://github.com/cobertura/cobertura) for code coverage
  - supported by [pytest-cov](https://pypi.org/project/pytest-cov/)

There are plans for an extension mechanism to support other summarizers soon.

## For More Information

For more information about this project, please [read our documentation](https://project-summarizer.readthedocs.io/en/latest/).

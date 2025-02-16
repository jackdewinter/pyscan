# TL;DR

Project Summarizer is a tool used to summarize various files produced by other tools
during a build or test process. This tool is intended to be executed after running
a test script or a build script. The benefit to using the Project Summarizer tool
is a quick summary of more terse information provided by other tools. The goal is
to provide the minimum level of feedback on changes to the project, avoiding a more
costly lookup of the summarized information. By meeting this goal, instead of looking
at a more complicated graph or web page, we hope to provide a 5 to 10 line summary
of the relevant information.

Our hope is that we can help developers achieve that goal at least 80 percent
of the time.

## Supported Summarizers

The currently supported summarizers are:

- [JUnit](https://junit.org/junit5/) for test results
    - supported by JUnit and [PyTest](https://docs.pytest.org/en/6.2.x/)
- [Cobertura](https://github.com/cobertura/cobertura) for code coverage
    - supported by [pytest-cov](https://pypi.org/project/pytest-cov/)

There is also an extension mechanism to support other summarizers.  However, so
far, we have not needed to implement any other summarizers.  If you have ideas for
summarizers that would fit in with the theme of this project, please contact us!

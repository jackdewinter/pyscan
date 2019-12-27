"""
Tests for the ...
"""
import os
import sys
import tempfile
from shutil import copyfile
from test.pytest_execute import InProcessExecution

# https://docs.pytest.org/en/latest/goodpractices.html#tests-outside-application-code
sys.path.insert(0, os.path.abspath("pymarkdown"))  # isort:skip
# pylint: disable=wrong-import-position
from pyscan.main import PyScan  # isort:skip


class MainlineExecutor(InProcessExecution):
    """
    Class to provide for a local instance of a InProcessExecution class.
    """

    def __init__(self):
        super().__init__()
        resource_directory = os.path.join(os.getcwd(), "test", "resources")
        assert os.path.exists(resource_directory)
        assert os.path.isdir(resource_directory)
        self.resource_directory = resource_directory

    def execute_main(self):
        PyScan().main()

    def get_main_name(self):
        return "main.py"


def test_get_summarizer_version():
    """
    Make sure that we can get information about the version of the summarizer.
    """

    # Arrange
    executor = MainlineExecutor()
    suppplied_arguments = ["--version"]

    expected_output = """\
main.py 0.1.0
"""
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_results = executor.invoke_main(arguments=suppplied_arguments, cwd=None)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def setup_directories():
    """
    Setup a temporary directory, a report directory under it (created if necessary),
    and the publish directory (not created if necessary).
    """

    temporary_work_directory = tempfile.TemporaryDirectory()
    report_directory = os.path.join(temporary_work_directory.name, "report")
    os.makedirs(report_directory)
    publish_directory = os.path.join(temporary_work_directory.name, "publish")
    return temporary_work_directory, report_directory, publish_directory


def compose_test_results(total_tests):
    """
    Given the right amounts for the various test totals, create a test results file
    for a report with only one class to test.
    """

    expected_test_results_file = (
        '{"projectName": "?", "reportSource": "pytest", "measurements": '
        + '[{"name": "test.test_scenarios", "totalTests": '
        + str(total_tests)
        + ', "failedTests": 0, '
        + '"errorTests": 0, "skippedTests": 0, "elapsedTimeInMilliseconds": 0}]}'
    )
    return expected_test_results_file


def test_summarize_simple_junit_report():
    """
    Test the summarizing of a simple junit report with no previous summary.
    """

    # Arrange
    executor = MainlineExecutor()
    temporary_work_directory, report_directory, publish_directory = setup_directories()
    junit_test_file = os.path.join(temporary_work_directory.name, "test.xml")
    copyfile(os.path.join(executor.resource_directory, "tests.xml"), junit_test_file)
    summary_result_file = os.path.join(report_directory, "test-results.json")

    suppplied_arguments = ["--junit", junit_test_file]

    expected_output = """\
Class Name            Total Tests   Failed Tests   Skipped Tests
-------------------  ------------  -------------  --------------
test.test_scenarios        3 (+3)              0               0
---                        -                   -               -
TOTALS                     3 (+3)              0               0
"""
    expected_error = ""
    expected_return_code = 0
    expected_test_results_file = compose_test_results(3)

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )
    execute_results.assert_resultant_file(
        summary_result_file, expected_test_results_file
    )
    return executor, temporary_work_directory, publish_directory, junit_test_file


def test_summarize_simple_junit_report_and_publish():
    """
    Test the summarizing of a simple junit report, then publishing that report.
    """

    # Arrange
    (
        executor,
        temporary_work_directory,
        publish_directory,
        junit_test_file,
    ) = test_summarize_simple_junit_report()
    summary_result_file = os.path.join(publish_directory, "test-results.json")

    suppplied_arguments = ["--publish"]

    expected_output = """\
Publish directory 'publish' does not exist.  Creating.
"""
    expected_error = ""
    expected_return_code = 0
    expected_test_results_file = compose_test_results(3)

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )
    execute_results.assert_resultant_file(
        summary_result_file, expected_test_results_file
    )

    return executor, temporary_work_directory, junit_test_file


def test_summarize_simple_junit_report_and_publish_and_summarize_again():
    """
    Test the summarizing of junit results, publishing, and then comparing again.
    """

    # Arrange
    (
        executor,
        temporary_work_directory,
        junit_test_file,
    ) = test_summarize_simple_junit_report_and_publish()

    suppplied_arguments = ["--junit", junit_test_file]

    expected_output = """\
Class Name            Total Tests   Failed Tests   Skipped Tests
-------------------  ------------  -------------  --------------
test.test_scenarios             3              0               0
---                             -              -               -
TOTALS                          3              0               0
"""
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )

def test_summarize_simple_junit_report_and_publish_and_then_test_fails():
    """
    Test the summarizing of junit results, publishing, and then comparing again with
    a test that fails.
    """

    # Arrange
    (
        executor,
        temporary_work_directory,
        junit_test_file,
    ) = test_summarize_simple_junit_report_and_publish()
    copyfile(os.path.join(executor.resource_directory, "tests-with-one-failure.xml"), junit_test_file)

    suppplied_arguments = ["--junit", junit_test_file]

    expected_output = """\
Class Name            Total Tests   Failed Tests   Skipped Tests
-------------------  ------------  -------------  --------------
test.test_scenarios             3         1 (+1)               0
---                             -         -                    -
TOTALS                          3         1 (+1)               0
"""
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )

def test_summarize_simple_junit_report_and_publish_and_then_test_skipped():
    """
    Test the summarizing of junit results, publishing, and then comparing again with
    a test that is skipped.
    """

    # Arrange
    (
        executor,
        temporary_work_directory,
        junit_test_file,
    ) = test_summarize_simple_junit_report_and_publish()
    copyfile(os.path.join(executor.resource_directory, "tests-with-one-skipped.xml"), junit_test_file)

    suppplied_arguments = ["--junit", junit_test_file]

    expected_output = """\
Class Name            Total Tests   Failed Tests   Skipped Tests
-------------------  ------------  -------------  --------------
test.test_scenarios             3              0          1 (+1)
---                             -              -          -
TOTALS                          3              0          1 (+1)
"""
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )

def test_summarize_simple_junit_report_and_publish_and_then_test_rename():
    """
    Test the summarizing of junit results, publishing, and then comparing again with
    the name of the test module being renamed.
    """

    # Arrange
    (
        executor,
        temporary_work_directory,
        junit_test_file,
    ) = test_summarize_simple_junit_report_and_publish()
    copyfile(os.path.join(executor.resource_directory, "tests-with-rename.xml"), junit_test_file)

    suppplied_arguments = ["--junit", junit_test_file]

    expected_output = """\
Class Name                 Total Tests   Failed Tests   Skipped Tests
------------------------  ------------  -------------  --------------
test.test_good_scenarios        3 (+3)              0               0
test.test_scenarios             - (-3)              -               -
---                             -                   -               -
TOTALS                          3                   0               0
"""
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )

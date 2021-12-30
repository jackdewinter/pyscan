"""
Tests for the basic scenarios for the scanner.
"""
import os
import sys
import tempfile
from test.pytest_execute import InProcessExecution

from project_summarizer.__main__ import main
from project_summarizer.main import ProjectSummarizer

JUNIT_COMMAND_LINE_FLAG = "--junit"
COBERTURA_COMMAND_LINE_FLAG = "--cobertura"

PUBLISH_COMMAND_LINE_FLAG = "--publish"
ONLY_CHANGES_COMMAND_LINE_FLAG = "--only-changes"

REPORT_DIRECTORY = "report"
PUBLISH_DIRECTORY = "publish"

JUNIT_RESULTS_FILE_NAME = "tests.xml"
RESULTS_SUMMARY_FILE_NAME = "test-results.json"
COVERAGE_SUMMARY_FILE_NAME = "coverage.json"

__COBERTURA_COVERAGE_FILE_NAME = "coverage.xml"
__COBERTURA_NON_WINDOWS_COVERAGE_FILE_NAME = "coverage-non-windows.xml"


def get_coverage_file_name():
    """
    Get the coverage file for the specific operating system class.

    This is needed as Windows uses a different file name hierarchy than the others.
    """
    if sys.platform.startswith("win"):
        return __COBERTURA_COVERAGE_FILE_NAME
    return __COBERTURA_NON_WINDOWS_COVERAGE_FILE_NAME


class MainlineExecutor(InProcessExecution):
    """
    Class to provide for a local instance of a InProcessExecution class.
    """

    def __init__(self, use_module=False, use_main=False):
        super().__init__()

        self.__use_main = use_main
        self.__entry_point = "__main.py__" if use_module else "main.py"

        resource_directory = os.path.join(os.getcwd(), "test", "resources")
        assert os.path.exists(resource_directory)
        assert os.path.isdir(resource_directory)
        self.resource_directory = resource_directory

    def execute_main(self):
        if self.__use_main:
            main()
        else:
            ProjectSummarizer().main()

    def get_main_name(self):
        return self.__entry_point


def test_get_summarizer_version():
    """
    Make sure that we can get information about the version of the summarizer.
    """

    # Arrange
    executor = MainlineExecutor()
    suppplied_arguments = ["--version"]

    expected_output = """\
main.py 0.5.0
"""
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_results = executor.invoke_main(arguments=suppplied_arguments, cwd=None)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


# pylint: disable=consider-using-with
def setup_directories(
    create_report_directory=True,
    create_publish_directory=False,
    temporary_work_directory=None,
):
    """
    Setup a temporary directory, a report directory under it (created if necessary),
    and the publish directory (not created by default if necessary).
    """

    if not temporary_work_directory:
        temporary_work_directory = tempfile.TemporaryDirectory()
    report_directory = os.path.join(temporary_work_directory.name, "report")
    if create_report_directory:
        os.makedirs(report_directory)
    publish_directory = os.path.join(temporary_work_directory.name, "publish")
    if create_publish_directory:
        os.makedirs(publish_directory)
    return temporary_work_directory, report_directory, publish_directory


# pylint: enable=consider-using-with

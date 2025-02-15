"""
Tests for the basic scenarios for the scanner.
"""

import os
import runpy
import sys
import tempfile
from test.pytest_execute import InProcessExecution

from project_summarizer.__main__ import main
from project_summarizer.main import ProjectSummarizer
from project_summarizer.plugin_manager.project_summarizer_plugin import (
    ProjectSummarizerPlugin,
)

JUNIT_COMMAND_LINE_FLAG = "--junit"
COBERTURA_COMMAND_LINE_FLAG = "--cobertura"

PUBLISH_COMMAND_LINE_FLAG = "--publish"
ONLY_CHANGES_COMMAND_LINE_FLAG = "--only-changes"

REPORT_DIRECTORY = ProjectSummarizerPlugin.DEFAULT_REPORT_PUBLISH_PATH
PUBLISH_DIRECTORY = ProjectSummarizerPlugin.DEFAULT_SUMMARY_PUBLISH_PATH

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

    version_path = os.path.join(".", "project_summarizer", "version.py")
    version_meta = runpy.run_path(version_path)
    semantic_version = version_meta["__version__"]

    expected_output = f"""
{semantic_version}
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
    alternate_publish_directory=None,
    temporary_work_directory=None,
):
    """
    Setup a temporary directory, a report directory under it (created if necessary),
    and the publish directory (not created by default if necessary).
    """

    if not temporary_work_directory:
        temporary_work_directory = tempfile.TemporaryDirectory()

    report_directory = os.path.join(
        temporary_work_directory.name,
        ProjectSummarizerPlugin.DEFAULT_REPORT_PUBLISH_PATH,
    )
    if create_report_directory:
        os.makedirs(report_directory)

    alternate_publish_directory = (
        alternate_publish_directory
        or ProjectSummarizerPlugin.DEFAULT_SUMMARY_PUBLISH_PATH
    )
    publish_directory = os.path.join(
        temporary_work_directory.name, alternate_publish_directory
    )
    if create_publish_directory:
        os.makedirs(publish_directory)

    return temporary_work_directory, report_directory, publish_directory


# pylint: enable=consider-using-with

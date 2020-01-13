"""
Tests for the basic scenarios for the scanner.
"""
import os
import sys
import tempfile
from test.pytest_execute import InProcessExecution

# https://docs.pytest.org/en/latest/goodpractices.html#tests-outside-application-code
sys.path.insert(0, os.path.abspath("pyscan"))  # isort:skip
# pylint: disable=wrong-import-position
from pyscan.main import PyScan  # isort:skip

JUNIT_COMMAND_LINE_FLAG = "--junit"
COBERTURA_COMMAND_LINE_FLAG = "--cobertura"

PUBLISH_COMMAND_LINE_FLAG = "--publish"
ONLY_CHANGES_COMMAND_LINE_FLAG = "--only-changes"


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

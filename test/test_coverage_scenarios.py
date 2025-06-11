"""
Tests to cover scenarios around the coverage measuring and reporting.
"""

import os
import platform
from shutil import copyfile
from test.patch_builtin_open import PatchBuiltinOpen
from test.pytest_execute import InProcessResult
from test.test_scenarios import (
    COBERTURA_COMMAND_LINE_FLAG,
    COVERAGE_SUMMARY_FILE_NAME,
    ONLY_CHANGES_COMMAND_LINE_FLAG,
    PUBLISH_COMMAND_LINE_FLAG,
    PUBLISH_DIRECTORY,
    MainlineExecutor,
    get_coverage_file_name,
    my_temporary_directory_impl,
    setup_directories2,
)
from typing import Tuple

_ = my_temporary_directory_impl


def compose_coverage_summary_file() -> str:
    """
    Create a test coverage file for a sample report.
    """

    return """{
    "projectName": "project_summarizer",
    "reportSource": "Coverage.py",
    "branchLevel": {
        "totalMeasured": 4,
        "totalCovered": 2
    },
    "lineLevel": {
        "totalMeasured": 15,
        "totalCovered": 10
    }
}
"""


def summarize_simple_cobertura_report(
    temporary_work_directory: str,
    create_publish_directory: bool = False,
) -> Tuple[MainlineExecutor, str, str]:
    """
    Test the summarizing of a simple cobertura report with no previous summary.
    """

    # Arrange
    executor = MainlineExecutor()
    report_directory, publish_directory = setup_directories2(
        create_publish_directory=create_publish_directory,
        temporary_work_directory=temporary_work_directory,
    )
    cobertura_coverage_file = os.path.join(
        temporary_work_directory, get_coverage_file_name()
    )
    copyfile(
        os.path.join(executor.resource_directory, get_coverage_file_name()),
        cobertura_coverage_file,
    )
    summary_coverage_file = os.path.join(report_directory, COVERAGE_SUMMARY_FILE_NAME)

    suppplied_arguments = [COBERTURA_COMMAND_LINE_FLAG, cobertura_coverage_file]

    expected_output = """

Test Coverage Summary
---------------------


  TYPE           COVERED  MEASURED      PERCENTAGE

  Instructions  --        --        -----
  Lines         10 (+10)  15 (+15)  66.67 (+66.67)
  Branches       2 ( +2)   4 ( +4)  50.00 (+50.00)
  Complexity    --        --        -----
  Methods       --        --        -----
  Classes       --        --        -----

"""
    expected_error = ""
    expected_return_code = 0
    expected_test_coverage_file = compose_coverage_summary_file()

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=temporary_work_directory
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )
    InProcessResult.assert_resultant_file(
        summary_coverage_file, expected_test_coverage_file
    )
    return (
        executor,
        publish_directory,
        cobertura_coverage_file,
    )


def test_summarize_simple_cobertura_report(my_temporary_directory: str) -> None:
    """
    Test the summarizing of a simple cobertura report with no previous summary.
    """
    summarize_simple_cobertura_report(my_temporary_directory)


def test_summarize_simple_cobertura_report_with_reduced_columns(
    my_temporary_directory: str,
    create_publish_directory: bool = False,
) -> None:
    """
    Test the summarizing of a simple cobertura report with no previous summary.
    """

    # Arrange
    executor = MainlineExecutor()
    report_directory, _ = setup_directories2(
        create_publish_directory=create_publish_directory,
        temporary_work_directory=my_temporary_directory,
    )
    cobertura_coverage_file = os.path.join(
        my_temporary_directory, get_coverage_file_name()
    )
    copyfile(
        os.path.join(executor.resource_directory, get_coverage_file_name()),
        cobertura_coverage_file,
    )
    summary_coverage_file = os.path.join(report_directory, COVERAGE_SUMMARY_FILE_NAME)

    suppplied_arguments = [
        COBERTURA_COMMAND_LINE_FLAG,
        cobertura_coverage_file,
        "--columns",
        "50",
    ]

    expected_output = """

Test Coverage Summary
---------------------


  TYPE           COVERED  MEASURED    PERCENTAGE

  Instructions  --        --        -----

  Lines         10 (+10)  15 (+15)  66.67 (+66.6
                                              7)
  Branches       2 ( +2)   4 ( +4)  50.00 (+50.0
                                              0)
  Complexity    --        --        -----

  Methods       --        --        -----

  Classes       --        --        -----



"""
    expected_error = ""
    expected_return_code = 0
    expected_test_coverage_file = compose_coverage_summary_file()

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=my_temporary_directory
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )
    InProcessResult.assert_resultant_file(
        summary_coverage_file, expected_test_coverage_file
    )


def test_summarize_simple_cobertura_report_with_quiet(
    my_temporary_directory: str,
    create_publish_directory: bool = False,
) -> None:
    """
    Test the summarizing of a simple cobertura report with no previous summary.
    """

    # Arrange
    executor = MainlineExecutor()
    report_directory, _ = setup_directories2(
        create_publish_directory=create_publish_directory,
        temporary_work_directory=my_temporary_directory,
    )
    cobertura_coverage_file = os.path.join(
        my_temporary_directory, get_coverage_file_name()
    )
    copyfile(
        os.path.join(executor.resource_directory, get_coverage_file_name()),
        cobertura_coverage_file,
    )
    summary_coverage_file = os.path.join(report_directory, COVERAGE_SUMMARY_FILE_NAME)

    suppplied_arguments = [
        COBERTURA_COMMAND_LINE_FLAG,
        cobertura_coverage_file,
        "--quiet",
    ]

    expected_output = ""
    expected_error = ""
    expected_return_code = 0
    expected_test_coverage_file = compose_coverage_summary_file()

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=my_temporary_directory
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )
    InProcessResult.assert_resultant_file(
        summary_coverage_file, expected_test_coverage_file
    )


def test_summarize_cobertura_report_with_bad_source(
    my_temporary_directory: str,
) -> None:
    """
    Test to make sure that summarizing a test coverage file that does not exist.
    """

    # Arrange
    executor = MainlineExecutor()
    setup_directories2(my_temporary_directory)
    cobertura_coverage_file = os.path.join(
        my_temporary_directory, get_coverage_file_name()
    )

    assert not os.path.exists(cobertura_coverage_file)
    suppplied_arguments = [COBERTURA_COMMAND_LINE_FLAG, cobertura_coverage_file]

    expected_output = (
        f"Project test coverage file '{cobertura_coverage_file}' does not exist.\n"
    )
    expected_error = ""
    expected_return_code = 1

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=my_temporary_directory
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_summarize_cobertura_report_with_source_as_directory(
    my_temporary_directory: str,
) -> None:
    """
    Test to make sure that summarizing a test coverage file that is not a file.
    """

    # Arrange
    executor = MainlineExecutor()
    setup_directories2(my_temporary_directory)
    cobertura_coverage_file = os.path.join(
        my_temporary_directory, get_coverage_file_name()
    )

    os.makedirs(cobertura_coverage_file)

    suppplied_arguments = [COBERTURA_COMMAND_LINE_FLAG, cobertura_coverage_file]

    expected_output = (
        f"Project test coverage file '{cobertura_coverage_file}' is not a file.\n"
    )
    expected_error = ""
    expected_return_code = 1

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=my_temporary_directory
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def summarize_simple_cobertura_report_and_publish(
    my_temporary_directory: str,
    check_file_contents: bool = True,
) -> Tuple[MainlineExecutor, str, str]:
    """
    NOTE: This function is in this module because of the other tests in this module
    that rely on it.  Moving it to the test_publish_scenarios module would create
    a circular reference.
    """

    # Arrange
    (
        executor,
        publish_directory,
        cobertura_coverage_file,
    ) = summarize_simple_cobertura_report(
        temporary_work_directory=my_temporary_directory
    )
    summary_coverage_file = os.path.join(publish_directory, COVERAGE_SUMMARY_FILE_NAME)

    suppplied_arguments = [PUBLISH_COMMAND_LINE_FLAG]

    expected_output = (
        f"Publish directory '{PUBLISH_DIRECTORY}' does not exist.  Creating.\n"
        + f"Published: {os.path.join(PUBLISH_DIRECTORY, COVERAGE_SUMMARY_FILE_NAME)}"
    )
    expected_error = ""
    expected_return_code = 0
    expected_test_coverage_file = compose_coverage_summary_file()

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=my_temporary_directory
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )
    if check_file_contents:
        InProcessResult.assert_resultant_file(
            summary_coverage_file, expected_test_coverage_file
        )

    return (
        executor,
        publish_directory,
        cobertura_coverage_file,
    )


def test_summarize_simple_cobertura_report_and_publish(
    my_temporary_directory: str,
) -> None:
    """
    Test the summarizing of a simple cobertura report, then publishing that report.
    """
    summarize_simple_cobertura_report_and_publish(my_temporary_directory)


def test_summarize_simple_cobertura_report_and_publish_and_summarize_again(
    my_temporary_directory: str,
    check_file_contents: bool = True,
) -> None:
    """
    Test the summarizing of a cobertura report, publishing, and then comparing again.
    """

    # Arrange
    (
        executor,
        _,
        cobertura_coverage_file,
    ) = summarize_simple_cobertura_report_and_publish(
        my_temporary_directory,
        check_file_contents=check_file_contents,
    )

    suppplied_arguments = [COBERTURA_COMMAND_LINE_FLAG, cobertura_coverage_file]

    expected_output = """

Test Coverage Summary
---------------------


  TYPE          COVERED  MEASURED  PERCENTAGE

  Instructions       --        --       -----
  Lines              10        15       66.67
  Branches            2         4       50.00
  Complexity         --        --       -----
  Methods            --        --       -----
  Classes            --        --       -----

"""
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=my_temporary_directory
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_summarize_simple_cobertura_report_and_publish_and_summarize_again_only_changes(
    my_temporary_directory: str,
    check_file_contents: bool = True,
) -> None:
    """
    Test the summarizing of a cobertura report, publishing, and then comparing again with the only changes flat set.
    """

    # Arrange
    (
        executor,
        _,
        cobertura_coverage_file,
    ) = summarize_simple_cobertura_report_and_publish(
        my_temporary_directory,
        check_file_contents=check_file_contents,
    )

    suppplied_arguments = [
        ONLY_CHANGES_COMMAND_LINE_FLAG,
        COBERTURA_COMMAND_LINE_FLAG,
        cobertura_coverage_file,
    ]

    expected_output = """

Test Coverage Summary
---------------------

Test coverage has not changed since last published test coverage.

"""
    expected_error = ""
    expected_return_code = 0

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=my_temporary_directory
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_summarize_bad_xml_test_coverage(my_temporary_directory: str) -> None:
    """
    Test the summarizing of cobertura results with a bad coverage file.
    """

    # Arrange
    executor = MainlineExecutor()
    setup_directories2(my_temporary_directory)
    cobertura_coverage_file = os.path.join(
        my_temporary_directory, get_coverage_file_name()
    )
    copyfile(
        os.path.join(executor.resource_directory, "coverage-bad.xml"),
        cobertura_coverage_file,
    )

    suppplied_arguments = [COBERTURA_COMMAND_LINE_FLAG, cobertura_coverage_file]

    expected_output = (
        f"Project test coverage file '{cobertura_coverage_file}' is not a "
        + "proper Cobertura-format test coverage file.\n"
    )
    expected_error = ""
    expected_return_code = 1

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=my_temporary_directory
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_summarize_bad_test_coverage(my_temporary_directory: str) -> None:
    """
    Test the summarizing of cobertura results with a bad coverage file.
    """

    # Arrange
    executor = MainlineExecutor()
    setup_directories2(my_temporary_directory)
    cobertura_coverage_file = os.path.join(
        my_temporary_directory, get_coverage_file_name()
    )
    copyfile(
        os.path.join(executor.resource_directory, "coverage-bad.txt"),
        cobertura_coverage_file,
    )

    suppplied_arguments = [COBERTURA_COMMAND_LINE_FLAG, cobertura_coverage_file]

    expected_output = f"Project test coverage file '{cobertura_coverage_file}' is not a valid test coverage file.\n"
    expected_error = ""
    expected_return_code = 1

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=my_temporary_directory
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_summarize_bad_report_directory(my_temporary_directory: str) -> None:
    """
    Test the summarizing of cobertura results with a bad report directory.
    """

    # Arrange
    executor = MainlineExecutor()
    setup_directories2(my_temporary_directory, create_report_directory=False)
    cobertura_coverage_file = os.path.join(
        my_temporary_directory, get_coverage_file_name()
    )
    copyfile(
        os.path.join(executor.resource_directory, get_coverage_file_name()),
        cobertura_coverage_file,
    )

    suppplied_arguments = [COBERTURA_COMMAND_LINE_FLAG, cobertura_coverage_file]

    expected_output = ""
    expected_error = """usage: main.py [-h] [--version] [--stack-trace] [--add-plugin ADD_PLUGIN]
               [--report-dir REPORT_DIR] [--publish-dir PUBLISH_DIR]
               [--cobertura path] [--junit path] [--only-changes] [--publish]
               [--quiet] [--columns DISPLAY_COLUMNS]
main.py: error: argument --report-dir: Path 'report' does not exist."""
    expected_return_code = 2

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=my_temporary_directory
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_summarize_invalid_published_summary_file(my_temporary_directory: str) -> None:
    """
    Test the summarizing of cobertura results with a bad report directory.
    """

    # Arrange
    executor = MainlineExecutor()
    _, publish_directory = setup_directories2(
        my_temporary_directory, create_publish_directory=True
    )
    cobertura_coverage_file = os.path.join(
        my_temporary_directory, get_coverage_file_name()
    )
    copyfile(
        os.path.join(executor.resource_directory, get_coverage_file_name()),
        cobertura_coverage_file,
    )
    summary_coverage_file = os.path.abspath(
        os.path.join(publish_directory, COVERAGE_SUMMARY_FILE_NAME)
    )
    if platform.system() == "Darwin" and not summary_coverage_file.startswith(
        "/private/"
    ):
        summary_coverage_file = f"/private{summary_coverage_file}"

    with open(summary_coverage_file, "w", encoding="utf-8") as outfile:
        outfile.write("this is not a json file")

    suppplied_arguments = [COBERTURA_COMMAND_LINE_FLAG, cobertura_coverage_file]

    expected_output = (
        f"Previous coverage summary file '{summary_coverage_file}' is not "
        + "a valid JSON file (Expecting value: line 1 column 1 (char 0))."
    )
    expected_error = ""
    expected_return_code = 1

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=my_temporary_directory
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_summarize_simple_cobertura_report_and_publish_and_summarize_with_error_on_publish_read(
    my_temporary_directory: str,
) -> None:
    """
    Test a summarize when trying to load a summary file from a previous run and getting
    an error when trying to write the summary report.
    """

    # Arrange
    (
        executor,
        publish_directory,
        cobertura_coverage_file,
    ) = summarize_simple_cobertura_report_and_publish(my_temporary_directory)

    suppplied_arguments = [COBERTURA_COMMAND_LINE_FLAG, cobertura_coverage_file]

    summary_coverage_file = os.path.join(publish_directory, COVERAGE_SUMMARY_FILE_NAME)
    summary_coverage_file = os.path.abspath(summary_coverage_file)
    if platform.system() == "Darwin" and not summary_coverage_file.startswith(
        "/private/"
    ):
        summary_coverage_file = f"/private{summary_coverage_file}"

    expected_output = f"Previous coverage summary file '{summary_coverage_file}' was not loaded (None).\n"
    expected_error = ""
    expected_return_code = 1

    # Act
    try:
        pbo = PatchBuiltinOpen()
        pbo.register_exception(summary_coverage_file, "r")
        pbo.start()

        execute_results = executor.invoke_main(
            arguments=suppplied_arguments, cwd=my_temporary_directory
        )
    finally:
        pbo.stop()

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_summarize_simple_cobertura_report_with_error_on_report_write(
    my_temporary_directory: str,
) -> None:
    """
    Test a summarize with an error when trying to write the summary report.
    """

    # Arrange
    executor = MainlineExecutor()
    report_directory, _ = setup_directories2(my_temporary_directory)
    cobertura_coverage_file = os.path.join(
        my_temporary_directory, get_coverage_file_name()
    )
    copyfile(
        os.path.join(executor.resource_directory, get_coverage_file_name()),
        cobertura_coverage_file,
    )
    summary_coverage_file = os.path.abspath(
        os.path.join(report_directory, COVERAGE_SUMMARY_FILE_NAME)
    )
    if platform.system() == "Darwin" and not summary_coverage_file.startswith(
        "/private/"
    ):
        summary_coverage_file = f"/private{summary_coverage_file}"

    suppplied_arguments = [COBERTURA_COMMAND_LINE_FLAG, cobertura_coverage_file]

    expected_output = (
        f"Project test coverage summary file '{os.path.abspath(summary_coverage_file)}' "
        + "was not written (None).\n"
    )
    expected_error = ""
    expected_return_code = 1

    # Act
    try:
        pbo = PatchBuiltinOpen()
        pbo.register_exception(os.path.abspath(summary_coverage_file), "w")
        pbo.start()

        execute_results = executor.invoke_main(
            arguments=suppplied_arguments, cwd=my_temporary_directory
        )
    finally:
        pbo.stop()

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )

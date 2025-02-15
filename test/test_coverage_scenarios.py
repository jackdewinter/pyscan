"""
Tests to cover scenarios around the coverage measuring and reporting.
"""

import os
import platform
from shutil import copyfile
from test.patch_builtin_open import PatchBuiltinOpen
from test.test_scenarios import (
    COBERTURA_COMMAND_LINE_FLAG,
    COVERAGE_SUMMARY_FILE_NAME,
    ONLY_CHANGES_COMMAND_LINE_FLAG,
    PUBLISH_COMMAND_LINE_FLAG,
    PUBLISH_DIRECTORY,
    MainlineExecutor,
    get_coverage_file_name,
    setup_directories,
)


def compose_coverage_summary_file():
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
    create_publish_directory=False, temporary_work_directory=None
):
    """
    Test the summarizing of a simple cobertura report with no previous summary.
    """

    # Arrange
    executor = MainlineExecutor()
    temporary_work_directory, report_directory, publish_directory = setup_directories(
        create_publish_directory=create_publish_directory,
        temporary_work_directory=temporary_work_directory,
    )
    cobertura_coverage_file = os.path.join(
        temporary_work_directory.name, get_coverage_file_name()
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
        arguments=suppplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )
    execute_results.assert_resultant_file(
        summary_coverage_file, expected_test_coverage_file
    )
    return (
        executor,
        temporary_work_directory,
        publish_directory,
        cobertura_coverage_file,
    )


def test_summarize_simple_cobertura_report():
    """
    Test the summarizing of a simple cobertura report with no previous summary.
    """
    summarize_simple_cobertura_report()


def test_summarize_simple_cobertura_report_with_reduced_columns(
    create_publish_directory=False, temporary_work_directory=None
):
    """
    Test the summarizing of a simple cobertura report with no previous summary.
    """

    # Arrange
    executor = MainlineExecutor()
    temporary_work_directory, report_directory, _ = setup_directories(
        create_publish_directory=create_publish_directory,
        temporary_work_directory=temporary_work_directory,
    )
    cobertura_coverage_file = os.path.join(
        temporary_work_directory.name, get_coverage_file_name()
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
        arguments=suppplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )
    execute_results.assert_resultant_file(
        summary_coverage_file, expected_test_coverage_file
    )


def test_summarize_simple_cobertura_report_with_quiet(
    create_publish_directory=False, temporary_work_directory=None
):
    """
    Test the summarizing of a simple cobertura report with no previous summary.
    """

    # Arrange
    executor = MainlineExecutor()
    temporary_work_directory, report_directory, _ = setup_directories(
        create_publish_directory=create_publish_directory,
        temporary_work_directory=temporary_work_directory,
    )
    cobertura_coverage_file = os.path.join(
        temporary_work_directory.name, get_coverage_file_name()
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
        arguments=suppplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )
    execute_results.assert_resultant_file(
        summary_coverage_file, expected_test_coverage_file
    )


def test_summarize_cobertura_report_with_bad_source():
    """
    Test to make sure that summarizing a test coverage file that does not exist.
    """

    # Arrange
    executor = MainlineExecutor()
    temporary_work_directory, _, _ = setup_directories()
    cobertura_coverage_file = os.path.join(
        temporary_work_directory.name, get_coverage_file_name()
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
        arguments=suppplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_summarize_cobertura_report_with_source_as_directory():
    """
    Test to make sure that summarizing a test coverage file that is not a file.
    """

    # Arrange
    executor = MainlineExecutor()
    temporary_work_directory, _, _ = setup_directories()
    cobertura_coverage_file = os.path.join(
        temporary_work_directory.name, get_coverage_file_name()
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
        arguments=suppplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def summarize_simple_cobertura_report_and_publish(
    temporary_work_directory=None, check_file_contents=True
):
    """
    NOTE: This function is in this module because of the other tests in this module
    that rely on it.  Moving it to the test_publish_scenarios module would create
    a circular reference.
    """

    # Arrange
    (
        executor,
        temporary_work_directory,
        publish_directory,
        cobertura_coverage_file,
    ) = summarize_simple_cobertura_report(
        temporary_work_directory=temporary_work_directory
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
        arguments=suppplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )
    if check_file_contents:
        execute_results.assert_resultant_file(
            summary_coverage_file, expected_test_coverage_file
        )

    return (
        executor,
        temporary_work_directory,
        publish_directory,
        cobertura_coverage_file,
    )


def test_summarize_simple_cobertura_report_and_publish():
    """
    Test the summarizing of a simple cobertura report, then publishing that report.
    """
    summarize_simple_cobertura_report_and_publish()


def test_summarize_simple_cobertura_report_and_publish_and_summarize_again(
    temporary_work_directory=None, check_file_contents=True
):
    """
    Test the summarizing of a cobertura report, publishing, and then comparing again.
    """

    # Arrange
    (
        executor,
        temporary_work_directory,
        _,
        cobertura_coverage_file,
    ) = summarize_simple_cobertura_report_and_publish(
        temporary_work_directory=temporary_work_directory,
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
        arguments=suppplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_summarize_simple_cobertura_report_and_publish_and_summarize_again_only_changes(
    temporary_work_directory=None, check_file_contents=True
):
    """
    Test the summarizing of a cobertura report, publishing, and then comparing again with the only changes flat set.
    """

    # Arrange
    (
        executor,
        temporary_work_directory,
        _,
        cobertura_coverage_file,
    ) = summarize_simple_cobertura_report_and_publish(
        temporary_work_directory=temporary_work_directory,
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
        arguments=suppplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_summarize_bad_xml_test_coverage():
    """
    Test the summarizing of cobertura results with a bad coverage file.
    """

    # Arrange
    executor = MainlineExecutor()
    temporary_work_directory, _, _ = setup_directories()
    cobertura_coverage_file = os.path.join(
        temporary_work_directory.name, get_coverage_file_name()
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
        arguments=suppplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_summarize_bad_test_coverage():
    """
    Test the summarizing of cobertura results with a bad coverage file.
    """

    # Arrange
    executor = MainlineExecutor()
    temporary_work_directory, _, _ = setup_directories()
    cobertura_coverage_file = os.path.join(
        temporary_work_directory.name, get_coverage_file_name()
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
        arguments=suppplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_summarize_bad_report_directory():
    """
    Test the summarizing of cobertura results with a bad report directory.
    """

    # Arrange
    executor = MainlineExecutor()
    temporary_work_directory, _, _ = setup_directories(create_report_directory=False)
    cobertura_coverage_file = os.path.join(
        temporary_work_directory.name, get_coverage_file_name()
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
        arguments=suppplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_summarize_invalid_published_summary_file():
    """
    Test the summarizing of cobertura results with a bad report directory.
    """

    # Arrange
    executor = MainlineExecutor()
    temporary_work_directory, _, publish_directory = setup_directories(
        create_publish_directory=True
    )
    cobertura_coverage_file = os.path.join(
        temporary_work_directory.name, get_coverage_file_name()
    )
    copyfile(
        os.path.join(executor.resource_directory, get_coverage_file_name()),
        cobertura_coverage_file,
    )
    summary_coverage_file = os.path.join(publish_directory, COVERAGE_SUMMARY_FILE_NAME)

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
        arguments=suppplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_summarize_simple_cobertura_report_and_publish_and_summarize_with_error_on_publish_read():
    """
    Test a summarize when trying to load a summary file from a previous run and getting
    an error when trying to write the summary report.
    """

    # Arrange
    (
        executor,
        temporary_work_directory,
        publish_directory,
        cobertura_coverage_file,
    ) = summarize_simple_cobertura_report_and_publish()

    suppplied_arguments = [COBERTURA_COMMAND_LINE_FLAG, cobertura_coverage_file]

    if platform.system() == "Darwin":
        print(f"-->publish_directory={publish_directory}")
    summary_coverage_file = os.path.join(publish_directory, COVERAGE_SUMMARY_FILE_NAME)
    if platform.system() == "Darwin":
        print(f"-->summary_coverage_file={summary_coverage_file}")
    summary_coverage_file = os.path.abspath(summary_coverage_file)
    if platform.system() == "Darwin":
        print(f"-->summary_coverage_file={summary_coverage_file}")

    expected_output = f"Previous coverage summary file '{summary_coverage_file}' was not loaded (None).\n"
    expected_error = ""
    expected_return_code = 1

    # Act
    try:
        pbo = PatchBuiltinOpen()
        if platform.system() == "Darwin":
            print(f"-->register_exception({summary_coverage_file})")
        pbo.register_exception(summary_coverage_file, "r")
        if platform.system() == "Darwin" and not summary_coverage_file.startswith(
            "/private/"
        ):
            xx = os.path.sep + os.path.join("private", summary_coverage_file)
            print(f"-->register_exception({xx})")
            pbo.register_exception(xx, "r")
        pbo.start()

        execute_results = executor.invoke_main(
            arguments=suppplied_arguments, cwd=temporary_work_directory.name
        )
    finally:
        if platform.system() == "Darwin":
            print(f"-->open_file_args={pbo.open_file_args}")
        pbo.stop()

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_summarize_simple_cobertura_report_with_error_on_report_write():
    """
    Test a summarize with an error when trying to write the summary report.
    """

    # Arrange
    executor = MainlineExecutor()
    temporary_work_directory, report_directory, _ = setup_directories()
    cobertura_coverage_file = os.path.join(
        temporary_work_directory.name, get_coverage_file_name()
    )
    copyfile(
        os.path.join(executor.resource_directory, get_coverage_file_name()),
        cobertura_coverage_file,
    )
    summary_coverage_file = os.path.join(report_directory, COVERAGE_SUMMARY_FILE_NAME)

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
            arguments=suppplied_arguments, cwd=temporary_work_directory.name
        )
    finally:
        pbo.stop()

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )

"""
Tests to cover scenarios around the measuring and reporting of test runs.
"""

import os
import platform
from shutil import copyfile
from test.patch_builtin_open import PatchBuiltinOpen
from test.pytest_execute import InProcessResult
from test.test_scenarios import (
    JUNIT_COMMAND_LINE_FLAG,
    JUNIT_RESULTS_FILE_NAME,
    ONLY_CHANGES_COMMAND_LINE_FLAG,
    PUBLISH_COMMAND_LINE_FLAG,
    PUBLISH_DIRECTORY,
    RESULTS_SUMMARY_FILE_NAME,
    MainlineExecutor,
    my_temporary_directory_impl,
    setup_directories2,
)
from typing import Optional, Tuple

from project_summarizer.plugin_manager.project_summarizer_plugin import (
    ProjectSummarizerPlugin,
)

_ = my_temporary_directory_impl

# pylint: disable=too-many-lines


def compose_test_results(total_tests: int) -> str:
    """
    Given the right amounts for the various test totals, create a test results file
    for a report with only one class to test.
    """

    return """{
    "projectName": "?",
    "reportSource": "pytest",
    "measurements": [
        {
            "name": "test.test_scenarios",
            "totalTests": {total_tests},
            "failedTests": 0,
            "errorTests": 0,
            "skippedTests": 0,
            "elapsedTimeInMilliseconds": 0
        }
    ]
}
""".replace(
        "{total_tests}", str(total_tests)
    )


def summarize_simple_junit_report(
    create_publish_directory: bool,
    temporary_work_directory: str,
    alternate_publish_directory: Optional[str] = None,
) -> Tuple[MainlineExecutor, str, str]:
    """
    Test the summarizing of a simple junit report with no previous summary.
    """

    # Arrange
    executor = MainlineExecutor()
    report_directory, publish_directory = setup_directories2(
        create_publish_directory=create_publish_directory,
        alternate_publish_directory=alternate_publish_directory,
        temporary_work_directory=temporary_work_directory,
    )
    junit_test_file = os.path.join(temporary_work_directory, JUNIT_RESULTS_FILE_NAME)
    copyfile(
        os.path.join(executor.resource_directory, JUNIT_RESULTS_FILE_NAME),
        junit_test_file,
    )
    summary_result_file = os.path.join(report_directory, RESULTS_SUMMARY_FILE_NAME)

    suppplied_arguments = [JUNIT_COMMAND_LINE_FLAG, junit_test_file]

    expected_output = """\

Test Results Summary
--------------------


  CLASS NAME           TOTAL TESTS  FAILED TESTS  SKIPPED TESTS

  test.test_scenarios       3 (+3)             0              0
  ---                       -                  -              -
  TOTALS                    3 (+3)             0              0
"""
    expected_error = ""
    expected_return_code = 0
    expected_test_results_file = compose_test_results(3)

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=temporary_work_directory
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )
    InProcessResult.assert_resultant_file(
        summary_result_file, expected_test_results_file
    )
    return executor, publish_directory, junit_test_file


def test_summarize_simple_junit_report(my_temporary_directory: str) -> None:
    """
    Test the summarizing of a simple junit report with no previous summary.
    """
    summarize_simple_junit_report(False, my_temporary_directory)


def test_summarize_simple_junit_report_with_reduced_columns(
    my_temporary_directory: str,
    create_publish_directory: bool = False,
) -> None:
    """
    Test the summarizing of a simple junit report with no previous summary with columns set.
    """

    # Arrange
    executor = MainlineExecutor()
    report_directory, _ = setup_directories2(
        create_publish_directory=create_publish_directory,
        temporary_work_directory=my_temporary_directory,
    )
    junit_test_file = os.path.join(my_temporary_directory, JUNIT_RESULTS_FILE_NAME)
    copyfile(
        os.path.join(executor.resource_directory, JUNIT_RESULTS_FILE_NAME),
        junit_test_file,
    )
    summary_result_file = os.path.join(report_directory, RESULTS_SUMMARY_FILE_NAME)

    suppplied_arguments = [JUNIT_COMMAND_LINE_FLAG, junit_test_file, "--columns", "50"]

    expected_output = """\

Test Results Summary
--------------------


  CLASS NAME  TOTAL TEST  FAILED TES  SKIPPED TE
                       S          TS         STS

  test.test_      3 (+3)           0           0
  scenarios
  ---             -                -           -
  TOTALS          3 (+3)           0           0

"""
    expected_error = ""
    expected_return_code = 0
    expected_test_results_file = compose_test_results(3)

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=my_temporary_directory
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )
    InProcessResult.assert_resultant_file(
        summary_result_file, expected_test_results_file
    )


def test_summarize_simple_junit_report_with_quiet(
    my_temporary_directory: str,
    create_publish_directory: bool = False,
) -> None:
    """
    Test the summarizing of a simple junit report with no previous summary with columns set.
    """

    # Arrange
    executor = MainlineExecutor()
    report_directory, _ = setup_directories2(
        create_publish_directory=create_publish_directory,
        temporary_work_directory=my_temporary_directory,
    )
    junit_test_file = os.path.join(my_temporary_directory, JUNIT_RESULTS_FILE_NAME)
    copyfile(
        os.path.join(executor.resource_directory, JUNIT_RESULTS_FILE_NAME),
        junit_test_file,
    )
    summary_result_file = os.path.join(report_directory, RESULTS_SUMMARY_FILE_NAME)

    suppplied_arguments = [JUNIT_COMMAND_LINE_FLAG, junit_test_file, "--quiet"]

    expected_output = ""
    expected_error = ""
    expected_return_code = 0
    expected_test_results_file = compose_test_results(3)

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=my_temporary_directory
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )
    InProcessResult.assert_resultant_file(
        summary_result_file, expected_test_results_file
    )


def test_summarize_junit_report_with_bad_source(my_temporary_directory: str) -> None:
    """
    Test to make sure that summarizing a test report file that does not exist.
    """

    # Arrange
    executor = MainlineExecutor()
    setup_directories2(my_temporary_directory)
    junit_test_file = os.path.join(my_temporary_directory, JUNIT_RESULTS_FILE_NAME)

    assert not os.path.exists(junit_test_file)
    suppplied_arguments = [JUNIT_COMMAND_LINE_FLAG, junit_test_file]

    expected_output = f"Project test report file '{junit_test_file}' does not exist.\n"
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


def test_summarize_junit_report_with_source_as_directory(
    my_temporary_directory: str,
) -> None:
    """
    Test to make sure that summarizing a test report file that is not a file.
    """

    # Arrange
    executor = MainlineExecutor()
    setup_directories2(my_temporary_directory)
    junit_test_file = os.path.join(my_temporary_directory, JUNIT_RESULTS_FILE_NAME)

    os.makedirs(junit_test_file)

    suppplied_arguments = [JUNIT_COMMAND_LINE_FLAG, junit_test_file]

    expected_output = f"Project test report file '{junit_test_file}' is not a file.\n"
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


def __test_summarize_simple_junit_report_and_publish(
    temporary_directory: str,
    check_file_contents: bool = True,
) -> Tuple[MainlineExecutor, str, str]:
    """
    Test the summarizing of a simple junit report, then publishing that report.

    NOTE: This function is in this module because of the other tests in this module
    that rely on it.  Moving it to the test_publish_scenarios module would create
    a circular reference.
    """

    # Arrange
    (
        executor,
        publish_directory,
        junit_test_file,
    ) = summarize_simple_junit_report(False, temporary_directory)
    summary_result_file = os.path.join(publish_directory, RESULTS_SUMMARY_FILE_NAME)

    suppplied_arguments = [PUBLISH_COMMAND_LINE_FLAG]

    expected_output = (
        f"Publish directory '{PUBLISH_DIRECTORY}' does not exist.  Creating.\n"
        + f"Published: {os.path.join(PUBLISH_DIRECTORY, RESULTS_SUMMARY_FILE_NAME)}"
    )
    expected_error = ""
    expected_return_code = 0
    expected_test_results_file = compose_test_results(3)

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=temporary_directory
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )
    if check_file_contents:
        InProcessResult.assert_resultant_file(
            summary_result_file, expected_test_results_file
        )

    return executor, publish_directory, junit_test_file


def test_summarize_simple_junit_report_and_publish(my_temporary_directory: str) -> None:
    """
    Test the summarizing of a simple junit report, then publishing that report.
    """
    __test_summarize_simple_junit_report_and_publish(my_temporary_directory)


def test_summarize_simple_junit_report_and_publish_and_summarize_again(
    my_temporary_directory: str,
    check_file_contents: bool = True,
) -> None:
    """
    Test the summarizing of junit results, publishing, and then comparing again.
    """

    # Arrange
    (
        executor,
        _,
        junit_test_file,
    ) = __test_summarize_simple_junit_report_and_publish(
        my_temporary_directory,
        check_file_contents=check_file_contents,
    )

    suppplied_arguments = [JUNIT_COMMAND_LINE_FLAG, junit_test_file]

    expected_output = """

Test Results Summary
--------------------


  CLASS NAME           TOTAL TESTS  FAILED TESTS  SKIPPED TESTS

  test.test_scenarios            3             0              0
  ---                            -             -              -
  TOTALS                         3             0              0
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


def test_summarize_simple_junit_report_and_publish_and_summarize_again_only_changes(
    my_temporary_directory: str,
) -> None:
    """
    Test the summarizing of junit results, publishing, and then comparing again with
    only changes enabled.
    """

    # Arrange
    (
        executor,
        _,
        junit_test_file,
    ) = __test_summarize_simple_junit_report_and_publish(my_temporary_directory)

    suppplied_arguments = [
        ONLY_CHANGES_COMMAND_LINE_FLAG,
        JUNIT_COMMAND_LINE_FLAG,
        junit_test_file,
    ]

    expected_output = """

Test Results Summary
--------------------

Test results have not changed since last published test results.
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


def test_summarize_simple_junit_report_and_publish_and_then_test_fails(
    my_temporary_directory: str,
) -> None:
    """
    Test the summarizing of junit results, publishing, and then comparing again with
    a test that fails.
    """

    # Arrange
    (
        executor,
        _,
        junit_test_file,
    ) = __test_summarize_simple_junit_report_and_publish(my_temporary_directory)
    copyfile(
        os.path.join(executor.resource_directory, "tests-with-one-failure.xml"),
        junit_test_file,
    )

    suppplied_arguments = [JUNIT_COMMAND_LINE_FLAG, junit_test_file]

    expected_output = """

Test Results Summary
--------------------


  CLASS NAME           TOTAL TESTS  FAILED TESTS  SKIPPED TESTS

  test.test_scenarios            3        1 (+1)              0
  ---                            -        -                   -
  TOTALS                         3        1 (+1)              0
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


def test_summarize_simple_junit_report_and_publish_and_then_new_test_only_changes(
    my_temporary_directory: str,
) -> None:
    """
    Test the summarizing of junit results, publishing, and then comparing again with
    a new test with only changes enabled.
    """

    # Arrange
    (
        executor,
        _,
        junit_test_file,
    ) = __test_summarize_simple_junit_report_and_publish(my_temporary_directory)
    copyfile(
        os.path.join(executor.resource_directory, "tests-with-new-test.xml"),
        junit_test_file,
    )

    suppplied_arguments = [
        ONLY_CHANGES_COMMAND_LINE_FLAG,
        JUNIT_COMMAND_LINE_FLAG,
        junit_test_file,
    ]

    expected_output = """

Test Results Summary
--------------------


  CLASS NAME           TOTAL TESTS  FAILED TESTS  SKIPPED TESTS

  test.test_scenarios       4 (+1)             0              0
  ---                       -                  -              -
  TOTALS                    4 (+1)             0              0
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


def test_summarize_simple_junit_report_and_publish_and_then_new_test_class_only_changes(
    my_temporary_directory: str,
) -> None:
    """
    Test the summarizing of junit results, publishing, and then comparing again with
    a new test in a new class with only changes enabled.
    """

    # Arrange
    (
        executor,
        _,
        junit_test_file,
    ) = __test_summarize_simple_junit_report_and_publish(my_temporary_directory)
    copyfile(
        os.path.join(executor.resource_directory, "tests-with-new-class-test.xml"),
        junit_test_file,
    )

    suppplied_arguments = [
        ONLY_CHANGES_COMMAND_LINE_FLAG,
        JUNIT_COMMAND_LINE_FLAG,
        junit_test_file,
    ]

    expected_output = """

Test Results Summary
--------------------


  CLASS NAME                 TOTAL TESTS  FAILED TESTS  SKIPPED TESTS

  test.test_other_scenarios       1 (+1)             0              0
  ---                             -                  -              -
  TOTALS                          4 (+1)             0              0
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


def test_summarize_simple_junit_report_and_publish_and_then_test_skipped(
    my_temporary_directory: str,
) -> None:
    """
    Test the summarizing of junit results, publishing, and then comparing again with
    a test that is skipped.
    """

    # Arrange
    (
        executor,
        _,
        junit_test_file,
    ) = __test_summarize_simple_junit_report_and_publish(my_temporary_directory)
    copyfile(
        os.path.join(executor.resource_directory, "tests-with-one-skipped.xml"),
        junit_test_file,
    )

    suppplied_arguments = [JUNIT_COMMAND_LINE_FLAG, junit_test_file]

    expected_output = """

Test Results Summary
--------------------


  CLASS NAME           TOTAL TESTS  FAILED TESTS  SKIPPED TESTS

  test.test_scenarios            3             0         1 (+1)
  ---                            -             -         -
  TOTALS                         3             0         1 (+1)
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


def test_summarize_simple_junit_report_and_publish_and_then_test_rename(
    my_temporary_directory: str,
) -> None:
    """
    Test the summarizing of junit results, publishing, and then comparing again with
    the name of the test module being renamed.
    """

    # Arrange
    (
        executor,
        _,
        junit_test_file,
    ) = __test_summarize_simple_junit_report_and_publish(my_temporary_directory)
    copyfile(
        os.path.join(executor.resource_directory, "tests-with-rename.xml"),
        junit_test_file,
    )

    suppplied_arguments = [JUNIT_COMMAND_LINE_FLAG, junit_test_file]

    expected_output = """

Test Results Summary
--------------------


  CLASS NAME                TOTAL TESTS  FAILED TESTS  SKIPPED TESTS

  test.test_good_scenarios       3 (+3)             0              0
  test.test_scenarios            - (-3)             -              -
  ---                            -                  -              -
  TOTALS                         3                  0              0
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


def test_summarize_single_and_double_digit_changes_from_published(
    my_temporary_directory: str,
) -> None:
    """
    Test the summarizing of junit results, publishing, and then comparing again with
    a large number of changes, both single and double digit changes.
    """

    # Arrange
    (
        executor,
        _,
        junit_test_file,
    ) = __test_summarize_simple_junit_report_and_publish(my_temporary_directory)
    copyfile(
        os.path.join(executor.resource_directory, "tests-with-lots-of-changes.xml"),
        junit_test_file,
    )

    suppplied_arguments = [JUNIT_COMMAND_LINE_FLAG, junit_test_file]

    expected_output = """

Test Results Summary
--------------------


  CLASS NAME           TOTAL TESTS  FAILED TESTS  SKIPPED TESTS

  test.test_scenarios      6  (+3)             0              0
  test.xtra_scenarios     10 (+10)             0              0
  ---                     --                   -              -
  TOTALS                  16 (+13)             0              0
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


def test_summarize_bad_xml_test_results(my_temporary_directory: str) -> None:
    """
    Test the summarizing of junit results with a bad test-results file.
    """

    # Arrange
    executor = MainlineExecutor()
    setup_directories2(my_temporary_directory)
    junit_test_file = os.path.join(my_temporary_directory, JUNIT_RESULTS_FILE_NAME)
    copyfile(
        os.path.join(executor.resource_directory, "tests-bad.xml"), junit_test_file
    )

    suppplied_arguments = [JUNIT_COMMAND_LINE_FLAG, junit_test_file]

    expected_output = f"Project test report file '{junit_test_file}' is not a proper Junit-format test report file.\n"
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


def test_summarize_bad_test_results(my_temporary_directory: str) -> None:
    """
    Test the summarizing of junit results with a bad test-results file.
    """

    # Arrange
    executor = MainlineExecutor()
    setup_directories2(my_temporary_directory)
    junit_test_file = os.path.join(my_temporary_directory, JUNIT_RESULTS_FILE_NAME)
    copyfile(
        os.path.join(executor.resource_directory, "tests-bad.txt"), junit_test_file
    )

    suppplied_arguments = [JUNIT_COMMAND_LINE_FLAG, junit_test_file]

    expected_output = f"Project test report file '{junit_test_file}' is not a valid test report file.\n"
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
    Test the summarizing of junit results with a bad report directory.
    """

    # Arrange
    executor = MainlineExecutor()
    setup_directories2(my_temporary_directory, create_report_directory=False)
    junit_test_file = os.path.join(my_temporary_directory, JUNIT_RESULTS_FILE_NAME)
    copyfile(
        os.path.join(executor.resource_directory, JUNIT_RESULTS_FILE_NAME),
        junit_test_file,
    )

    suppplied_arguments = [JUNIT_COMMAND_LINE_FLAG, junit_test_file]

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
    Test the summarizing of junit results with a bad report directory.
    """

    # Arrange
    executor = MainlineExecutor()
    _, publish_directory = setup_directories2(
        my_temporary_directory, create_publish_directory=True
    )
    junit_test_file = os.path.join(my_temporary_directory, JUNIT_RESULTS_FILE_NAME)
    copyfile(
        os.path.join(executor.resource_directory, JUNIT_RESULTS_FILE_NAME),
        junit_test_file,
    )
    summary_result_file = os.path.join(publish_directory, RESULTS_SUMMARY_FILE_NAME)

    with open(
        summary_result_file, "w", encoding=ProjectSummarizerPlugin.DEFAULT_FILE_ENCODING
    ) as outfile:
        outfile.write("this is not a json file")

    suppplied_arguments = [JUNIT_COMMAND_LINE_FLAG, junit_test_file]

    file_name = os.path.join(PUBLISH_DIRECTORY, RESULTS_SUMMARY_FILE_NAME)

    expected_output = (
        f"Previous results summary file '{file_name}' is "
        + "not a valid JSON file (Expecting value: line 1 column 1 (char 0))."
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


def test_summarize_simple_junit_report_and_publish_and_summarize_with_error_on_publish_read(
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
        junit_test_file,
    ) = __test_summarize_simple_junit_report_and_publish(my_temporary_directory)

    suppplied_arguments = [JUNIT_COMMAND_LINE_FLAG, junit_test_file]

    file_name = os.path.join(PUBLISH_DIRECTORY, RESULTS_SUMMARY_FILE_NAME)

    expected_output = (
        f"Previous results summary file '{file_name}' was not loaded (None).\n"
    )
    expected_error = ""
    expected_return_code = 1

    summary_result_file = os.path.abspath(
        os.path.join(publish_directory, RESULTS_SUMMARY_FILE_NAME)
    )
    if platform.system() == "Darwin" and not summary_result_file.startswith(
        "/private/"
    ):
        summary_result_file = f"/private{summary_result_file}"

    # Act
    try:
        pbo = PatchBuiltinOpen()
        pbo.register_exception(summary_result_file, "r")
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


def test_summarize_simple_junit_report_with_error_on_report_write(
    my_temporary_directory: str,
) -> None:
    """
    Test a summarize with an error when trying to write the summary report.
    """

    # Arrange
    executor = MainlineExecutor()
    report_directory, _ = setup_directories2(my_temporary_directory)
    junit_test_file = os.path.join(my_temporary_directory, JUNIT_RESULTS_FILE_NAME)
    copyfile(
        os.path.join(executor.resource_directory, JUNIT_RESULTS_FILE_NAME),
        junit_test_file,
    )
    summary_result_file = os.path.abspath(
        os.path.join(report_directory, RESULTS_SUMMARY_FILE_NAME)
    )
    if platform.system() == "Darwin" and not summary_result_file.startswith(
        "/private/"
    ):
        summary_result_file = f"/private{summary_result_file}"

    suppplied_arguments = [JUNIT_COMMAND_LINE_FLAG, junit_test_file]

    expected_output = (
        f"Project test report summary file '{os.path.abspath(summary_result_file)}' "
        + "was not written (None).\n"
    )
    expected_error = ""
    expected_return_code = 1

    # Act
    try:
        pbo = PatchBuiltinOpen()
        pbo.register_exception(os.path.abspath(summary_result_file), "w")
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


def test_sample_1(my_temporary_directory: str) -> None:
    """
    Test the summarizing of junit results against a previous published version.
    This was encountered during development, and the test case captured.
    """

    # Arrange
    executor = MainlineExecutor()
    _, publish_directory = setup_directories2(my_temporary_directory)
    junit_test_file = os.path.join(my_temporary_directory, JUNIT_RESULTS_FILE_NAME)
    summary_result_file = os.path.join(publish_directory, RESULTS_SUMMARY_FILE_NAME)

    copyfile(
        os.path.join(executor.resource_directory, "tests-sample-1.xml"),
        junit_test_file,
    )

    os.makedirs(publish_directory)
    previous_test_summary_contents = (
        '{"projectName": "?", "reportSource": "pytest", '
        + '"measurements": ['
        + '{"name": "test.test_coverage_scenarios", "totalTests": 14, "failedTests": 0, '
        + '"errorTests": 0, "skippedTests": 0, "elapsedTimeInMilliseconds": 0}, '
        + '{"name": "test.test_scenarios", "totalTests": 23, "failedTests": 0, '
        + '"errorTests": 0, "skippedTests": 0, "elapsedTimeInMilliseconds": 0}'
        + "]}"
    )
    with open(
        summary_result_file, "w", encoding=ProjectSummarizerPlugin.DEFAULT_FILE_ENCODING
    ) as outfile:
        outfile.write(previous_test_summary_contents)

    suppplied_arguments = [JUNIT_COMMAND_LINE_FLAG, junit_test_file]

    expected_output = """

Test Results Summary
--------------------


  CLASS NAME                    TOTAL TESTS  FAILED TESTS  SKIPPED TESTS

  test.test_coverage_scenarios     12  (-2)             0              0
  test.test_publish_scenarios       9  (+9)             0              0
  test.test_results_scenarios      18 (+18)             0              0
  test.test_scenarios               1 (-22)             0              0
  ---                              --                   -              -
  TOTALS                           40  (+3)             0              0

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

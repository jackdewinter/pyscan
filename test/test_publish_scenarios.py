"""
Tests to cover scenarios around the publishing of summaries.
"""
import os
from shutil import copyfile
from test.patch_builtin_open import PatchBuiltinOpen
from test.test_coverage_scenarios import (
    COBERTURA_COVERAGE_FILE_NAME,
    COVERAGE_SUMMARY_FILE_NAME,
    compose_coverage_summary_file,
    test_summarize_simple_cobertura_report,
)
from test.test_results_scenarios import (
    JUNIT_RESULTS_FILE_NAME,
    RESULTS_SUMMARY_FILE_NAME,
    compose_test_results,
    test_summarize_simple_junit_report,
)
from test.test_scenarios import (
    PUBLISH_COMMAND_LINE_FLAG,
    MainlineExecutor,
    setup_directories,
)


def test_summarize_simple_junit_report_and_publish_with_existing_publish():
    """
    Test to make sure that publishing with a publish directory that already exists.
    """

    # Arrange
    (
        executor,
        temporary_work_directory,
        publish_directory,
        _,
    ) = test_summarize_simple_junit_report(create_publish_directory=True)
    summary_result_file = os.path.join(publish_directory, RESULTS_SUMMARY_FILE_NAME)

    suppplied_arguments = [PUBLISH_COMMAND_LINE_FLAG]

    expected_output = ""
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


def test_summarize_simple_cobertura_report_and_publish_with_existing_publish():
    """
    Test to make sure that publishing with a publish directory that already exists.
    """

    # Arrange
    (
        executor,
        temporary_work_directory,
        publish_directory,
        _,
    ) = test_summarize_simple_cobertura_report(create_publish_directory=True)
    summary_coverage_file = os.path.join(publish_directory, COVERAGE_SUMMARY_FILE_NAME)

    suppplied_arguments = [PUBLISH_COMMAND_LINE_FLAG]

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


def test_publish_with_existing_publish_as_file():
    """
    Test to make sure that publishing with a publish directory that exists as a file.
    """

    # Arrange
    executor = MainlineExecutor()
    temporary_work_directory, _, publish_directory = setup_directories()

    with open(publish_directory, "w", encoding="utf-8") as outfile:
        outfile.write("test")

    suppplied_arguments = [PUBLISH_COMMAND_LINE_FLAG]

    expected_output = """\
Publish directory 'publish' already exists, but as a file.
"""
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


def test_publish_with_test_file_as_directory():
    """
    Test to make sure that publishing with a test results summary file that is not a file fails.
    """

    # Arrange
    executor = MainlineExecutor()
    temporary_work_directory, report_directory, _ = setup_directories()
    junit_test_file = os.path.join(
        temporary_work_directory.name, JUNIT_RESULTS_FILE_NAME
    )
    copyfile(os.path.join(executor.resource_directory, "tests.xml"), junit_test_file)
    summary_result_file = os.path.join(report_directory, RESULTS_SUMMARY_FILE_NAME)

    os.makedirs(summary_result_file)

    suppplied_arguments = [PUBLISH_COMMAND_LINE_FLAG]

    results_path = os.path.join("report", RESULTS_SUMMARY_FILE_NAME)
    expected_output = f"Test results summary path '{results_path}' is not a file.\n"
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


def test_publish_with_coverage_file_as_directory():
    """
    Test to make sure that publishing with a test coverage summary file that is not a file fails.
    """

    # Arrange
    executor = MainlineExecutor()
    temporary_work_directory, report_directory, _ = setup_directories()
    cobertura_coverage_file = os.path.join(
        temporary_work_directory.name, COBERTURA_COVERAGE_FILE_NAME
    )
    copyfile(
        os.path.join(executor.resource_directory, COBERTURA_COVERAGE_FILE_NAME),
        cobertura_coverage_file,
    )
    summary_coverage_file = os.path.join(report_directory, COVERAGE_SUMMARY_FILE_NAME)

    os.makedirs(summary_coverage_file)

    suppplied_arguments = [PUBLISH_COMMAND_LINE_FLAG]

    coverage_path = os.path.join("report", COVERAGE_SUMMARY_FILE_NAME)
    expected_output = f"Test coverage summary path '{coverage_path}' is not a file.\n"
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


def test_summarize_simple_junit_report_and_publish_with_error_on_source_read():
    """
    Test a summarize and publish with the source reading failing on open.
    """

    # Arrange
    (
        executor,
        temporary_work_directory,
        _,
        _,
    ) = test_summarize_simple_junit_report(create_publish_directory=True)

    suppplied_arguments = [PUBLISH_COMMAND_LINE_FLAG]

    results_path = os.path.join("report", RESULTS_SUMMARY_FILE_NAME)
    expected_output = f"Publishing file '{results_path}' failed (None).\n"
    expected_error = ""
    expected_return_code = 1

    # Act
    try:
        pbo = PatchBuiltinOpen()
        pbo.register_exception(results_path, "rb")
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


def test_summarize_simple_junit_report_and_publish_with_error_on_destination_write():
    """
    Test a summarize and publish with the destination write failing on open.
    """

    # Arrange
    (
        executor,
        temporary_work_directory,
        _,
        _,
    ) = test_summarize_simple_junit_report(create_publish_directory=True)

    suppplied_arguments = [PUBLISH_COMMAND_LINE_FLAG]

    results_path = os.path.join("report", RESULTS_SUMMARY_FILE_NAME)
    expected_output = f"Publishing file '{results_path}' failed (None).\n"
    expected_error = ""
    expected_return_code = 1

    # Act
    try:
        pbo = PatchBuiltinOpen()
        pbo.register_exception("publish\\test-results.json", "wb")
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

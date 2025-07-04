"""
Tests to cover scenarios around the publishing of summaries.
"""

import os
from shutil import copyfile
from test.patch_builtin_open import PatchBuiltinOpen
from test.pytest_execute import InProcessResult
from test.test_coverage_scenarios import (
    compose_coverage_summary_file,
    summarize_simple_cobertura_report,
)
from test.test_results_scenarios import (
    compose_test_results,
    summarize_simple_junit_report,
)
from test.test_scenarios import (
    COVERAGE_SUMMARY_FILE_NAME,
    JUNIT_RESULTS_FILE_NAME,
    PUBLISH_COMMAND_LINE_FLAG,
    PUBLISH_DIRECTORY,
    REPORT_DIRECTORY,
    RESULTS_SUMMARY_FILE_NAME,
    MainlineExecutor,
    get_coverage_file_name,
    my_temporary_directory_impl,
    setup_directories2,
)

from project_summarizer.plugin_manager.project_summarizer_plugin import (
    ProjectSummarizerPlugin,
)

_ = my_temporary_directory_impl


def test_summarize_simple_junit_report_and_publish_with_existing_publish(
    my_temporary_directory: str,
) -> None:
    """
    Test to make sure that publishing with a publish directory that already exists.
    """

    # Arrange
    (
        executor,
        publish_directory,
        _,
    ) = summarize_simple_junit_report(
        create_publish_directory=True, temporary_work_directory=my_temporary_directory
    )
    summary_result_file = os.path.join(publish_directory, RESULTS_SUMMARY_FILE_NAME)

    suppplied_arguments = [PUBLISH_COMMAND_LINE_FLAG]
    publish_path = os.path.join(
        ProjectSummarizerPlugin.DEFAULT_SUMMARY_PUBLISH_PATH, "test-results.json"
    )

    expected_output = f"Published: {publish_path}"
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


def test_summarize_simple_junit_report_and_publish_with_alternate_publish(
    my_temporary_directory: str,
) -> None:
    """
    Test to make sure that publishing with a publish directory that already exists.
    """

    # Arrange
    alternate_publish_directory = "alt-publish"
    (
        executor,
        publish_directory,
        _,
    ) = summarize_simple_junit_report(
        create_publish_directory=True,
        temporary_work_directory=my_temporary_directory,
        alternate_publish_directory=alternate_publish_directory,
    )
    summary_result_file = os.path.join(publish_directory, RESULTS_SUMMARY_FILE_NAME)

    suppplied_arguments = [
        PUBLISH_COMMAND_LINE_FLAG,
        "--publish-dir",
        alternate_publish_directory,
    ]

    expected_output = f"Published: {os.path.join(alternate_publish_directory, RESULTS_SUMMARY_FILE_NAME)}"
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


def test_summarize_simple_cobertura_report_and_publish_with_existing_publish(
    my_temporary_directory: str,
) -> None:
    """
    Test to make sure that publishing with a publish directory that already exists.
    """

    # Arrange
    (
        executor,
        publish_directory,
        _,
    ) = summarize_simple_cobertura_report(
        my_temporary_directory, create_publish_directory=True
    )
    summary_coverage_file = os.path.join(publish_directory, COVERAGE_SUMMARY_FILE_NAME)

    suppplied_arguments = [PUBLISH_COMMAND_LINE_FLAG]

    output_file = os.path.join(
        ProjectSummarizerPlugin.DEFAULT_SUMMARY_PUBLISH_PATH, COVERAGE_SUMMARY_FILE_NAME
    )
    expected_output = f"Published: {output_file}"
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


def test_publish_with_existing_publish_as_file(my_temporary_directory: str) -> None:
    """
    Test to make sure that publishing with a publish directory that exists as a file.
    """

    # Arrange
    executor = MainlineExecutor()
    _, publish_directory = setup_directories2(my_temporary_directory)

    with open(
        publish_directory, "w", encoding=ProjectSummarizerPlugin.DEFAULT_FILE_ENCODING
    ) as outfile:
        outfile.write("test")

    suppplied_arguments = [PUBLISH_COMMAND_LINE_FLAG]

    expected_output = (
        f"Publish directory '{PUBLISH_DIRECTORY}' already exists, but as a file."
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


def test_publish_with_test_file_as_directory(my_temporary_directory: str) -> None:
    """
    Test to make sure that publishing with a test results summary file that is not a file fails.
    """

    # Arrange
    executor = MainlineExecutor()
    report_directory, _ = setup_directories2(my_temporary_directory)
    junit_test_file = os.path.join(my_temporary_directory, JUNIT_RESULTS_FILE_NAME)
    copyfile(
        os.path.join(executor.resource_directory, JUNIT_RESULTS_FILE_NAME),
        junit_test_file,
    )
    summary_result_file = os.path.join(report_directory, RESULTS_SUMMARY_FILE_NAME)

    os.makedirs(summary_result_file)

    suppplied_arguments = [PUBLISH_COMMAND_LINE_FLAG]

    results_path = os.path.join(REPORT_DIRECTORY, RESULTS_SUMMARY_FILE_NAME)
    expected_output = ""
    expected_error = f"Summary path '{results_path}' is not a file."
    expected_return_code = 1

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=my_temporary_directory
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_publish_with_coverage_file_as_directory(my_temporary_directory: str) -> None:
    """
    Test to make sure that publishing with a test coverage summary file that is not a file fails.
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
    summary_coverage_file = os.path.join(report_directory, COVERAGE_SUMMARY_FILE_NAME)

    os.makedirs(summary_coverage_file)

    suppplied_arguments = [PUBLISH_COMMAND_LINE_FLAG]

    coverage_path = os.path.join(REPORT_DIRECTORY, COVERAGE_SUMMARY_FILE_NAME)
    expected_output = ""
    expected_error = f"Summary path '{coverage_path}' is not a file."
    expected_return_code = 1

    # Act
    execute_results = executor.invoke_main(
        arguments=suppplied_arguments, cwd=my_temporary_directory
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_summarize_simple_junit_report_and_publish_with_error_on_source_read(
    my_temporary_directory: str,
) -> None:
    """
    Test a summarize and publish with the source reading failing on open.
    """

    # Arrange
    (
        executor,
        _,
        _,
    ) = summarize_simple_junit_report(
        create_publish_directory=True, temporary_work_directory=my_temporary_directory
    )

    suppplied_arguments = [PUBLISH_COMMAND_LINE_FLAG]

    results_path = os.path.join(REPORT_DIRECTORY, RESULTS_SUMMARY_FILE_NAME)
    expected_output = f"Publishing file '{results_path}' failed (None).\n"
    expected_error = ""
    expected_return_code = 1

    # Act
    pbo = PatchBuiltinOpen()
    try:
        pbo.register_exception(results_path, "rb")
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


def test_summarize_simple_junit_report_and_publish_with_error_on_destination_write(
    my_temporary_directory: str,
) -> None:
    """
    Test a summarize and publish with the destination write failing on open.
    """

    # Arrange
    (
        executor,
        _,
        _,
    ) = summarize_simple_junit_report(
        create_publish_directory=True, temporary_work_directory=my_temporary_directory
    )

    suppplied_arguments = [PUBLISH_COMMAND_LINE_FLAG]

    results_path = os.path.join(REPORT_DIRECTORY, RESULTS_SUMMARY_FILE_NAME)
    expected_output = f"Publishing file '{results_path}' failed (None).\n"
    expected_error = ""
    expected_return_code = 1

    file_name = os.path.join(PUBLISH_DIRECTORY, RESULTS_SUMMARY_FILE_NAME)

    # Act
    pbo = PatchBuiltinOpen()
    try:
        pbo.register_exception(file_name, "wb")
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

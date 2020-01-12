"""
Tests to cover scenarios around the coverage measuring and reporting.
"""
import os
from shutil import copyfile
from test.test_scenarios import MainlineExecutor, setup_directories


def compose_test_results():
    """
    Given the right amounts for the various test totals, create a test results file
    for a report with only one class to test.
    """

    expected_test_results_file = """{"projectName": "pyscan", "reportSource": "pytest", "branchLevel": {"totalMeasured": 4, "totalCovered": 2}, "lineLevel": {"totalMeasured": 15, "totalCovered": 10}}"""
    return expected_test_results_file


def test_summarize_simple_cobertura_report(
    create_publish_directory=False, temporary_work_directory=None
):
    """
    Test the summarizing of a simple junit report with no previous summary.
    """

    # Arrange
    executor = MainlineExecutor()
    temporary_work_directory, report_directory, publish_directory = setup_directories(
        create_publish_directory=create_publish_directory,
        temporary_work_directory=temporary_work_directory,
    )
    cobertura_test_file = os.path.join(temporary_work_directory.name, "coverage.xml")
    copyfile(
        os.path.join(executor.resource_directory, "coverage.xml"), cobertura_test_file
    )
    summary_result_file = os.path.join(report_directory, "coverage.json")

    suppplied_arguments = ["--cobertura", cobertura_test_file]

    expected_output = """\

Coverage Results Summary
------------------------

Type           Covered   Measured      Percentage
------------  --------  ---------  --------------
Instructions  --         --        -----
Lines         10 (+10)   15 (+15)  66.67 (+66.67)
Branches       2 ( +2)    4 ( +4)  50.00 (+50.00)
Complexity    --         --        -----
Methods       --         --        -----
Classes       --         --        -----

"""
    expected_error = ""
    expected_return_code = 0
    expected_test_results_file = compose_test_results()

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
    return executor, temporary_work_directory, publish_directory, cobertura_test_file


def test_summarize_simple_cobertura_report_and_publish(
    temporary_work_directory=None, check_file_contents=True
):
    """
    Test the summarizing of a simple cobertura report, then publishing that report.
    """

    # Arrange
    (
        executor,
        temporary_work_directory,
        publish_directory,
        cobertura_test_file,
    ) = test_summarize_simple_cobertura_report(
        temporary_work_directory=temporary_work_directory
    )
    summary_result_file = os.path.join(publish_directory, "coverage.json")

    suppplied_arguments = ["--publish"]

    expected_output = """\
Publish directory 'publish' does not exist.  Creating.
"""
    expected_error = ""
    expected_return_code = 0
    expected_test_results_file = compose_test_results()

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
            summary_result_file, expected_test_results_file
        )

    return executor, temporary_work_directory, publish_directory, cobertura_test_file


def test_summarize_simple_junit_report_and_publish_with_existing_publish(
    temporary_work_directory=None,
):
    """
    Test to make sure that publishing with a publish directory that already exists.
    """

    # Arrange
    (
        executor,
        temporary_work_directory,
        publish_directory,
        cobertura_test_file,
    ) = test_summarize_simple_cobertura_report(
        create_publish_directory=True, temporary_work_directory=temporary_work_directory
    )
    summary_result_file = os.path.join(publish_directory, "coverage.json")

    suppplied_arguments = ["--publish"]

    expected_output = """\
"""
    expected_error = ""
    expected_return_code = 0
    expected_test_results_file = compose_test_results()

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

    return executor, temporary_work_directory, cobertura_test_file


def test_summarize_simple_cobertura_report_and_publish_and_summarize_again(
    temporary_work_directory=None, check_file_contents=True
):
    """
    Test the summarizing of junit results, publishing, and then comparing again.
    """

    # Arrange
    (
        executor,
        temporary_work_directory,
        _,
        cobertura_test_file,
    ) = test_summarize_simple_cobertura_report_and_publish(
        temporary_work_directory=temporary_work_directory,
        check_file_contents=check_file_contents,
    )

    suppplied_arguments = ["--cobertura", cobertura_test_file]

    expected_output = """\

Coverage Results Summary
------------------------

Type           Covered   Measured    Percentage
------------  --------  ---------  ------------
Instructions    --         --      -----
Lines           10 (0)     15 (0)  66.67 (0.00)
Branches         2 (0)      4 (0)  50.00 (0.00)
Complexity      --         --      -----
Methods         --         --      -----
Classes         --         --      -----

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
    Test the summarizing of junit results, publishing, and then comparing again.
    """

    # Arrange
    (
        executor,
        temporary_work_directory,
        _,
        cobertura_test_file,
    ) = test_summarize_simple_cobertura_report_and_publish(
        temporary_work_directory=temporary_work_directory,
        check_file_contents=check_file_contents,
    )

    suppplied_arguments = ["--only-changes", "--cobertura", cobertura_test_file]

    expected_output = """\

Coverage Results Summary
------------------------

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

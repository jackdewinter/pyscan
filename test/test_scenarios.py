"""
Tests for the ...
"""
import os
import sys
import tempfile
from shutil import copyfile
from test.patch_builtin_open import PatchBuiltinOpen
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


def test_summarize_simple_junit_report(
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
    junit_test_file = os.path.join(temporary_work_directory.name, "test.xml")
    copyfile(os.path.join(executor.resource_directory, "tests.xml"), junit_test_file)
    summary_result_file = os.path.join(report_directory, "test-results.json")

    suppplied_arguments = ["--junit", junit_test_file]

    expected_output = """\

Test Results Summary
--------------------

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


def test_summarize_junit_report_with_bad_source():
    """
    Test to make sure that summarizing a test report file that does not exist.
    """

    # Arrange
    executor = MainlineExecutor()
    temporary_work_directory, _, publish_directory = setup_directories()
    junit_test_file = os.path.join(temporary_work_directory.name, "test.xml")

    assert not os.path.exists(junit_test_file)
    suppplied_arguments = ["--junit", junit_test_file]

    expected_output = (
        "Project test report file '" + junit_test_file + "' does not exist.\n"
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
    return executor, temporary_work_directory, publish_directory, junit_test_file


def test_summarize_junit_report_with_source_as_directory():
    """
    Test to make sure that summarizing a test report file that is not a file.
    """

    # Arrange
    executor = MainlineExecutor()
    temporary_work_directory, _, publish_directory = setup_directories()
    junit_test_file = os.path.join(temporary_work_directory.name, "test.xml")

    os.makedirs(junit_test_file)

    suppplied_arguments = ["--junit", junit_test_file]

    expected_output = (
        "Project test report file '" + junit_test_file + "' is not a file.\n"
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
    return executor, temporary_work_directory, publish_directory, junit_test_file


def test_summarize_simple_junit_report_and_publish(
    temporary_work_directory=None, check_file_contents=True
):
    """
    Test the summarizing of a simple junit report, then publishing that report.
    """

    # Arrange
    (
        executor,
        temporary_work_directory,
        publish_directory,
        junit_test_file,
    ) = test_summarize_simple_junit_report(
        temporary_work_directory=temporary_work_directory
    )
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
    if check_file_contents:
        execute_results.assert_resultant_file(
            summary_result_file, expected_test_results_file
        )

    return executor, temporary_work_directory, publish_directory, junit_test_file


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
        junit_test_file,
    ) = test_summarize_simple_junit_report(
        create_publish_directory=True, temporary_work_directory=temporary_work_directory
    )
    summary_result_file = os.path.join(publish_directory, "test-results.json")

    suppplied_arguments = ["--publish"]

    expected_output = """\
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


def test_publish_with_existing_publish_as_file():
    """
    Test to make sure that publishing with a publish directory that exists as a file.
    """

    # Arrange
    (
        executor,
        temporary_work_directory,
        publish_directory,
        junit_test_file,
    ) = test_summarize_simple_junit_report()
    os.path.join(publish_directory, "test-results.json")

    with open(publish_directory, "w") as outfile:
        outfile.write("test")

    suppplied_arguments = ["--publish"]

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

    return executor, temporary_work_directory, junit_test_file


def test_publish_with_no_test_file_as_directory():
    """
    Test to make sure that publishing with a test results summary file that is not a file fails.
    """

    # Arrange
    executor = MainlineExecutor()
    temporary_work_directory, report_directory, _ = setup_directories()
    junit_test_file = os.path.join(temporary_work_directory.name, "test.xml")
    copyfile(os.path.join(executor.resource_directory, "tests.xml"), junit_test_file)
    summary_result_file = os.path.join(report_directory, "test-results.json")

    os.makedirs(summary_result_file)

    suppplied_arguments = ["--publish"]

    results_path = os.path.join("report", "test-results.json")
    expected_output = (
        "Test results summary path '" + results_path + "' is not a file.\n"
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

    return executor, temporary_work_directory, junit_test_file


def test_summarize_simple_junit_report_and_publish_and_summarize_again(
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
        junit_test_file,
    ) = test_summarize_simple_junit_report_and_publish(
        temporary_work_directory=temporary_work_directory,
        check_file_contents=check_file_contents,
    )

    suppplied_arguments = ["--junit", junit_test_file]

    expected_output = """\

Test Results Summary
--------------------

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


def test_summarize_simple_junit_report_and_publish_and_summarize_again_only_changes():
    """
    Test the summarizing of junit results, publishing, and then comparing again with
    only changes enabled.
    """

    # Arrange
    (
        executor,
        temporary_work_directory,
        _,
        junit_test_file,
    ) = test_summarize_simple_junit_report_and_publish()

    suppplied_arguments = ["--only-changes", "--junit", junit_test_file]

    expected_output = """\

Test Results Summary
--------------------

Test results have not changed since last published test results.
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
        _,
        junit_test_file,
    ) = test_summarize_simple_junit_report_and_publish()
    copyfile(
        os.path.join(executor.resource_directory, "tests-with-one-failure.xml"),
        junit_test_file,
    )

    suppplied_arguments = ["--junit", junit_test_file]

    expected_output = """\

Test Results Summary
--------------------

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


def test_summarize_simple_junit_report_and_publish_and_then_new_test_only_changes():
    """
    Test the summarizing of junit results, publishing, and then comparing again with
    a new test with only changes enabled.
    """

    # Arrange
    (
        executor,
        temporary_work_directory,
        _,
        junit_test_file,
    ) = test_summarize_simple_junit_report_and_publish()
    copyfile(
        os.path.join(executor.resource_directory, "tests-with-new-test.xml"),
        junit_test_file,
    )

    suppplied_arguments = ["--only-changes", "--junit", junit_test_file]

    expected_output = """\

Test Results Summary
--------------------

Class Name            Total Tests   Failed Tests   Skipped Tests
-------------------  ------------  -------------  --------------
test.test_scenarios        4 (+1)              0               0
---                        -                   -               -
TOTALS                     4 (+1)              0               0
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


def test_summarize_simple_junit_report_and_publish_and_then_new_test_class_only_changes():
    """
    Test the summarizing of junit results, publishing, and then comparing again with
    a new test in a new class with only changes enabled.
    """

    # Arrange
    (
        executor,
        temporary_work_directory,
        _,
        junit_test_file,
    ) = test_summarize_simple_junit_report_and_publish()
    copyfile(
        os.path.join(executor.resource_directory, "tests-with-new-class-test.xml"),
        junit_test_file,
    )

    suppplied_arguments = ["--only-changes", "--junit", junit_test_file]

    expected_output = """\

Test Results Summary
--------------------

Class Name                  Total Tests   Failed Tests   Skipped Tests
-------------------------  ------------  -------------  --------------
test.test_other_scenarios        1 (+1)              0               0
---                              -                   -               -
TOTALS                           4 (+1)              0               0
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
        _,
        junit_test_file,
    ) = test_summarize_simple_junit_report_and_publish()
    copyfile(
        os.path.join(executor.resource_directory, "tests-with-one-skipped.xml"),
        junit_test_file,
    )

    suppplied_arguments = ["--junit", junit_test_file]

    expected_output = """\

Test Results Summary
--------------------

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
        _,
        junit_test_file,
    ) = test_summarize_simple_junit_report_and_publish()
    copyfile(
        os.path.join(executor.resource_directory, "tests-with-rename.xml"),
        junit_test_file,
    )

    suppplied_arguments = ["--junit", junit_test_file]

    expected_output = """\

Test Results Summary
--------------------

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


def test_summarize_bad_xml_test_results():
    """
    Test the summarizing of junit results with a bad test-results file.
    """

    # Arrange
    executor = MainlineExecutor()
    temporary_work_directory, _, _ = setup_directories()
    junit_test_file = os.path.join(temporary_work_directory.name, "test.xml")
    copyfile(
        os.path.join(executor.resource_directory, "tests-bad.xml"), junit_test_file
    )

    suppplied_arguments = ["--junit", junit_test_file]

    expected_output = (
        "Project test report file '"
        + junit_test_file
        + "' is not a proper Junit-format test report file.\n"
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


def test_summarize_bad_test_results():
    """
    Test the summarizing of junit results with a bad test-results file.
    """

    # Arrange
    executor = MainlineExecutor()
    temporary_work_directory, _, _ = setup_directories()
    junit_test_file = os.path.join(temporary_work_directory.name, "test.xml")
    copyfile(
        os.path.join(executor.resource_directory, "tests-bad.txt"), junit_test_file
    )

    suppplied_arguments = ["--junit", junit_test_file]

    expected_output = (
        "Project test report file '"
        + junit_test_file
        + "' is not a valid test report file.\n"
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


def test_summarize_bad_report_directory():
    """
    Test the summarizing of junit results with a bad report directory.
    """

    # Arrange
    executor = MainlineExecutor()
    temporary_work_directory, _, _ = setup_directories(create_report_directory=False)
    junit_test_file = os.path.join(temporary_work_directory.name, "test.xml")
    copyfile(os.path.join(executor.resource_directory, "tests.xml"), junit_test_file)

    suppplied_arguments = ["--junit", junit_test_file]

    expected_output = """\
Summary output path 'report' does not exist.
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


def test_summarize_invalid_published_summary_file():
    """
    Test the summarizing of junit results with a bad report directory.
    """

    # Arrange
    executor = MainlineExecutor()
    temporary_work_directory, _, publish_directory = setup_directories(
        create_publish_directory=True
    )
    junit_test_file = os.path.join(temporary_work_directory.name, "test.xml")
    copyfile(os.path.join(executor.resource_directory, "tests.xml"), junit_test_file)
    summary_result_file = os.path.join(publish_directory, "test-results.json")

    with open(summary_result_file, "w") as outfile:
        outfile.write("this is not a json file")

    suppplied_arguments = ["--junit", junit_test_file]

    expected_output = """\
Previous summary file 'publish\\test-results.json' is not a valid JSON file (Expecting value: line 1 column 1 (char 0)).
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


def test_summarize_simple_junit_report_and_publish_and_summarize_with_error_on_publish_read():
    """
    Test a summarize when trying to load a summary file from a previous run and getting
    an error when trying to write the summary report.
    """

    # Arrange
    (
        executor,
        temporary_work_directory,
        publish_directory,
        junit_test_file,
    ) = test_summarize_simple_junit_report_and_publish()

    suppplied_arguments = ["--junit", junit_test_file]

    expected_output = (
        "Previous summary file 'publish\\test-results.json' was not loaded (None).\n"
    )
    expected_error = ""
    expected_return_code = 1

    summary_result_file = os.path.join(publish_directory, "test-results.json")

    # Act
    try:
        pbo = PatchBuiltinOpen()
        pbo.register_exception(summary_result_file, "r")
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


def test_summarize_simple_junit_report_with_error_on_report_write():
    """
    Test a summarize with an error when trying to write the summary report.
    """

    # Arrange
    executor = MainlineExecutor()
    temporary_work_directory, report_directory, _ = setup_directories()
    junit_test_file = os.path.join(temporary_work_directory.name, "test.xml")
    copyfile(os.path.join(executor.resource_directory, "tests.xml"), junit_test_file)
    summary_result_file = os.path.join(report_directory, "test-results.json")

    suppplied_arguments = ["--junit", junit_test_file]

    expected_output = (
        "Project test summary file '"
        + os.path.abspath(summary_result_file)
        + "' was not written (None).\n"
    )
    expected_error = ""
    expected_return_code = 1

    # Act
    try:
        pbo = PatchBuiltinOpen()
        pbo.register_exception(os.path.abspath(summary_result_file), "w")
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


def test_summarize_simple_junit_report_and_publish_with_error_on_source_read():
    """
    Test a summarize and publish with the source reading failing on open.
    """

    # Arrange
    (executor, temporary_work_directory, _, _,) = test_summarize_simple_junit_report(
        create_publish_directory=True
    )

    suppplied_arguments = ["--publish"]

    results_path = os.path.join("report", "test-results.json")
    expected_output = "Publishing file '" + results_path + "' failed (None).\n"
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
    (executor, temporary_work_directory, _, _,) = test_summarize_simple_junit_report(
        create_publish_directory=True
    )

    suppplied_arguments = ["--publish"]

    results_path = os.path.join("report", "test-results.json")
    expected_output = "Publishing file '" + results_path + "' failed (None).\n"
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

"""
Module to provide tests related to the basic parts of the scanner.
"""
import os
from test.test_scenarios import MainlineExecutor, setup_directories


def test_scanner_with_no_parameters():
    """
    Test to make sure we get the simple information if no parameters are supplied.
    """

    # Arrange
    scanner = MainlineExecutor()
    temporary_work_directory, _, _ = setup_directories()
    supplied_arguments = []

    expected_return_code = 2
    expected_output = """Error: Either --publish or one of the reporting arguments mush be specified.
usage: main.py [-h] [--version] [--stack-trace] [--add-plugin ADD_PLUGIN]
               [--report-dir REPORT_DIR] [--publish-dir PUBLISH_DIR]
               [--cobertura path] [--junit path] [--only-changes] [--publish]
               [--quiet] [--columns DISPLAY_COLUMNS]

Summarize Python files.

optional arguments:
  -h, --help            Show this help message and exit.
  --version             Show program's version number and exit.
  --stack-trace         if an error occurs, print out the stack trace for
                        debug purposes
  --add-plugin ADD_PLUGIN
                        Add a plugin file to provide additional project
                        summaries.
  --report-dir REPORT_DIR
                        Directory to generate the summary reports in.
  --publish-dir PUBLISH_DIR
                        Directory to publish the summary reports to.
  --cobertura path      Source file name for cobertura test coverage
                        reporting.
  --junit path          Source file name for junit test result reporting.
  --only-changes        Only the summary items that have changed are displayed
                        in the console summary.
  --publish             Publish the summaries to the publish directory and
                        exit.
  --quiet               The report summary files will be generated, but no
                        summary will be output to the console.
  --columns DISPLAY_COLUMNS
                        Specifies the number of character columns to use in
                        the console summary."""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(
        arguments=supplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scanner_with_no_parameters_through_module():
    """
    Test to make sure we get the simple information if no parameters are supplied,
    but through the module interface.
    """

    # Arrange
    scanner = MainlineExecutor(use_module=True)
    temporary_work_directory, _, _ = setup_directories()
    supplied_arguments = []

    expected_return_code = 2
    expected_error = ""
    expected_output = """Error: Either --publish or one of the reporting arguments mush be specified.
usage: __main.py__ [-h] [--version] [--stack-trace] [--add-plugin ADD_PLUGIN]
                   [--report-dir REPORT_DIR] [--publish-dir PUBLISH_DIR]
                   [--cobertura path] [--junit path] [--only-changes]
                   [--publish] [--quiet] [--columns DISPLAY_COLUMNS]

Summarize Python files.

optional arguments:
  -h, --help            Show this help message and exit.
  --version             Show program's version number and exit.
  --stack-trace         if an error occurs, print out the stack trace for
                        debug purposes
  --add-plugin ADD_PLUGIN
                        Add a plugin file to provide additional project
                        summaries.
  --report-dir REPORT_DIR
                        Directory to generate the summary reports in.
  --publish-dir PUBLISH_DIR
                        Directory to publish the summary reports to.
  --cobertura path      Source file name for cobertura test coverage
                        reporting.
  --junit path          Source file name for junit test result reporting.
  --only-changes        Only the summary items that have changed are displayed
                        in the console summary.
  --publish             Publish the summaries to the publish directory and
                        exit.
  --quiet               The report summary files will be generated, but no
                        summary will be output to the console.
  --columns DISPLAY_COLUMNS
                        Specifies the number of character columns to use in
                        the console summary."""

    # Act
    execute_results = scanner.invoke_main(
        arguments=supplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scanner_with_no_parameters_through_main():
    """
    Test to make sure we get the simple information if no parameters are supplied,
    but through the main interface.
    """

    # Arrange
    scanner = MainlineExecutor(use_main=True)
    temporary_work_directory, _, _ = setup_directories()
    supplied_arguments = []

    expected_return_code = 2
    expected_output = """Error: Either --publish or one of the reporting arguments mush be specified.
usage: main.py [-h] [--version] [--stack-trace] [--add-plugin ADD_PLUGIN]
               [--report-dir REPORT_DIR] [--publish-dir PUBLISH_DIR]
               [--cobertura path] [--junit path] [--only-changes] [--publish]
               [--quiet] [--columns DISPLAY_COLUMNS]

Summarize Python files.

optional arguments:
  -h, --help            Show this help message and exit.
  --version             Show program's version number and exit.
  --stack-trace         if an error occurs, print out the stack trace for
                        debug purposes
  --add-plugin ADD_PLUGIN
                        Add a plugin file to provide additional project
                        summaries.
  --report-dir REPORT_DIR
                        Directory to generate the summary reports in.
  --publish-dir PUBLISH_DIR
                        Directory to publish the summary reports to.
  --cobertura path      Source file name for cobertura test coverage
                        reporting.
  --junit path          Source file name for junit test result reporting.
  --only-changes        Only the summary items that have changed are displayed
                        in the console summary.
  --publish             Publish the summaries to the publish directory and
                        exit.
  --quiet               The report summary files will be generated, but no
                        summary will be output to the console.
  --columns DISPLAY_COLUMNS
                        Specifies the number of character columns to use in
                        the console summary."""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(
        arguments=supplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scanner_with_dash_h():
    """
    Test to make sure we get help if '-h' is supplied.
    """

    # Arrange
    scanner = MainlineExecutor()
    temporary_work_directory, _, _ = setup_directories()
    supplied_arguments = ["-h"]

    expected_return_code = 0
    expected_output = """usage: main.py [-h] [--version] [--stack-trace] [--add-plugin ADD_PLUGIN]
               [--report-dir REPORT_DIR] [--publish-dir PUBLISH_DIR]
               [--cobertura path] [--junit path] [--only-changes] [--publish]
               [--quiet] [--columns DISPLAY_COLUMNS]

Summarize Python files.

optional arguments:
  -h, --help            Show this help message and exit.
  --version             Show program's version number and exit.
  --stack-trace         if an error occurs, print out the stack trace for
                        debug purposes
  --add-plugin ADD_PLUGIN
                        Add a plugin file to provide additional project
                        summaries.
  --report-dir REPORT_DIR
                        Directory to generate the summary reports in.
  --publish-dir PUBLISH_DIR
                        Directory to publish the summary reports to.
  --cobertura path      Source file name for cobertura test coverage
                        reporting.
  --junit path          Source file name for junit test result reporting.
  --only-changes        Only the summary items that have changed are displayed
                        in the console summary.
  --publish             Publish the summaries to the publish directory and
                        exit.
  --quiet               The report summary files will be generated, but no
                        summary will be output to the console.
  --columns DISPLAY_COLUMNS
                        Specifies the number of character columns to use in
                        the console summary."""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(
        arguments=supplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scanner_with_dash_dash_quiet():
    """
    Test to make sure we get help if '--quiet' is supplied.
    """

    # Arrange
    scanner = MainlineExecutor()
    temporary_work_directory, _, _ = setup_directories()
    supplied_arguments = ["--quiet"]

    expected_return_code = 2
    expected_output = """Error: Either --publish or one of the reporting arguments mush be specified.
usage: main.py [-h] [--version] [--stack-trace] [--add-plugin ADD_PLUGIN]
               [--report-dir REPORT_DIR] [--publish-dir PUBLISH_DIR]
               [--cobertura path] [--junit path] [--only-changes] [--publish]
               [--quiet] [--columns DISPLAY_COLUMNS]

Summarize Python files.

optional arguments:
  -h, --help            Show this help message and exit.
  --version             Show program's version number and exit.
  --stack-trace         if an error occurs, print out the stack trace for
                        debug purposes
  --add-plugin ADD_PLUGIN
                        Add a plugin file to provide additional project
                        summaries.
  --report-dir REPORT_DIR
                        Directory to generate the summary reports in.
  --publish-dir PUBLISH_DIR
                        Directory to publish the summary reports to.
  --cobertura path      Source file name for cobertura test coverage
                        reporting.
  --junit path          Source file name for junit test result reporting.
  --only-changes        Only the summary items that have changed are displayed
                        in the console summary.
  --publish             Publish the summaries to the publish directory and
                        exit.
  --quiet               The report summary files will be generated, but no
                        summary will be output to the console.
  --columns DISPLAY_COLUMNS
                        Specifies the number of character columns to use in
                        the console summary."""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(
        arguments=supplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scanner_with_dash_dash_columns():
    """
    Test to make sure we get help if '--columns' is supplied without a number.
    """

    # Arrange
    scanner = MainlineExecutor()
    temporary_work_directory, _, _ = setup_directories()
    supplied_arguments = ["--columns"]

    expected_return_code = 2
    expected_output = ""
    expected_error = """usage: main.py [-h] [--version] [--stack-trace] [--add-plugin ADD_PLUGIN]
               [--report-dir REPORT_DIR] [--publish-dir PUBLISH_DIR]
               [--cobertura path] [--junit path] [--only-changes] [--publish]
               [--quiet] [--columns DISPLAY_COLUMNS]
main.py: error: argument --columns: expected one argument"""

    # Act
    execute_results = scanner.invoke_main(
        arguments=supplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scanner_with_dash_dash_columns_good_number():
    """
    Test to make sure we get help if '--columns' is supplied with a good number.
    """

    # Arrange
    scanner = MainlineExecutor()
    temporary_work_directory, _, _ = setup_directories()

    supplied_arguments = ["--columns", "100"]
    expected_return_code = 2
    expected_output = """Error: Either --publish or one of the reporting arguments mush be specified.
usage: main.py [-h] [--version] [--stack-trace] [--add-plugin ADD_PLUGIN]
               [--report-dir REPORT_DIR] [--publish-dir PUBLISH_DIR]
               [--cobertura path] [--junit path] [--only-changes] [--publish]
               [--quiet] [--columns DISPLAY_COLUMNS]

Summarize Python files.

optional arguments:
  -h, --help            Show this help message and exit.
  --version             Show program's version number and exit.
  --stack-trace         if an error occurs, print out the stack trace for
                        debug purposes
  --add-plugin ADD_PLUGIN
                        Add a plugin file to provide additional project
                        summaries.
  --report-dir REPORT_DIR
                        Directory to generate the summary reports in.
  --publish-dir PUBLISH_DIR
                        Directory to publish the summary reports to.
  --cobertura path      Source file name for cobertura test coverage
                        reporting.
  --junit path          Source file name for junit test result reporting.
  --only-changes        Only the summary items that have changed are displayed
                        in the console summary.
  --publish             Publish the summaries to the publish directory and
                        exit.
  --quiet               The report summary files will be generated, but no
                        summary will be output to the console.
  --columns DISPLAY_COLUMNS
                        Specifies the number of character columns to use in
                        the console summary."""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(
        arguments=supplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scanner_with_dash_dash_columns_bad_number():
    """
    Test to make sure we get help if '--columns' is supplied with a bad number.
    """

    # Arrange
    scanner = MainlineExecutor()
    temporary_work_directory, _, _ = setup_directories()
    supplied_arguments = ["--columns", "20"]

    expected_return_code = 2
    expected_output = ""
    expected_error = """usage: main.py [-h] [--version] [--stack-trace] [--add-plugin ADD_PLUGIN]
               [--report-dir REPORT_DIR] [--publish-dir PUBLISH_DIR]
               [--cobertura path] [--junit path] [--only-changes] [--publish]
               [--quiet] [--columns DISPLAY_COLUMNS]
main.py: error: argument --columns: Value '20' is not an integer between between 50 and 200."""

    # Act
    execute_results = scanner.invoke_main(
        arguments=supplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scanner_with_dash_dash_report_dir_with_non_existant():
    """
    Test to make sure we get help if '--report-dir' is supplied with a non-existant directory.
    """

    # Arrange
    scanner = MainlineExecutor()
    temporary_work_directory, _, _ = setup_directories()
    supplied_arguments = ["--report-dir", "alternate-reports"]

    assert not os.path.exists("alternate-reports")

    expected_return_code = 2
    expected_output = ""
    expected_error = """usage: main.py [-h] [--version] [--stack-trace] [--add-plugin ADD_PLUGIN]
               [--report-dir REPORT_DIR] [--publish-dir PUBLISH_DIR]
               [--cobertura path] [--junit path] [--only-changes] [--publish]
               [--quiet] [--columns DISPLAY_COLUMNS]
main.py: error: argument --report-dir: Path 'alternate-reports' does not exist.
"""

    # Act
    execute_results = scanner.invoke_main(
        arguments=supplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_scanner_with_dash_dash_report_dir_with_non_directory():
    """
    Test to make sure we get help if '--report-dir' is supplied with a file instead of a directory.
    """

    # Arrange
    scanner = MainlineExecutor()
    temporary_work_directory, _, _ = setup_directories()
    assert os.path.exists("README.md") and os.path.isfile("README.md")
    readme_path = os.path.abspath("README.md")
    supplied_arguments = ["--report-dir", readme_path]

    expected_return_code = 2
    expected_output = ""
    expected_error = """usage: main.py [-h] [--version] [--stack-trace] [--add-plugin ADD_PLUGIN]
               [--report-dir REPORT_DIR] [--publish-dir PUBLISH_DIR]
               [--cobertura path] [--junit path] [--only-changes] [--publish]
               [--quiet] [--columns DISPLAY_COLUMNS]
main.py: error: argument --report-dir: Path '{path}' is not an existing directory.
""".replace(
        "{path}", readme_path
    )

    # Act
    execute_results = scanner.invoke_main(
        arguments=supplied_arguments, cwd=temporary_work_directory.name
    )

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )

"""
Module to provide tests related to the basic parts of the scanner.
"""

from test.test_scenarios import MainlineExecutor


def test_scanner_with_no_parameters():
    """
    Test to make sure we get the simple information if no parameters are supplied.
    """

    # Arrange
    scanner = MainlineExecutor()
    supplied_arguments = []

    expected_return_code = 2
    expected_output = """usage: main.py [-h] [--version] [--cobertura path] [--junit path]
               [--only-changes] [--publish] [--quiet]
               [--columns DISPLAY_COLUMNS]

Summarize Python files.

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --cobertura path      source file name for cobertura test coverage reporting
  --junit path          source file name for junit test result reporting
  --only-changes        only_changes
  --publish             publish
  --quiet               quiet_mode
  --columns DISPLAY_COLUMNS
                        display_columns"""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

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
    supplied_arguments = []

    expected_return_code = 2
    expected_output = """usage: __main.py__ [-h] [--version] [--cobertura path] [--junit path]
                   [--only-changes] [--publish] [--quiet]
                   [--columns DISPLAY_COLUMNS]

Summarize Python files.

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --cobertura path      source file name for cobertura test coverage reporting
  --junit path          source file name for junit test result reporting
  --only-changes        only_changes
  --publish             publish
  --quiet               quiet_mode
  --columns DISPLAY_COLUMNS
                        display_columns"""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

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
    supplied_arguments = []

    expected_return_code = 2
    expected_output = """usage: main.py [-h] [--version] [--cobertura path] [--junit path]
               [--only-changes] [--publish] [--quiet]
               [--columns DISPLAY_COLUMNS]

Summarize Python files.

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --cobertura path      source file name for cobertura test coverage reporting
  --junit path          source file name for junit test result reporting
  --only-changes        only_changes
  --publish             publish
  --quiet               quiet_mode
  --columns DISPLAY_COLUMNS
                        display_columns"""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

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
    supplied_arguments = ["-h"]

    expected_return_code = 0
    expected_output = """usage: main.py [-h] [--version] [--cobertura path] [--junit path]
               [--only-changes] [--publish] [--quiet]
               [--columns DISPLAY_COLUMNS]

Summarize Python files.

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --cobertura path      source file name for cobertura test coverage reporting
  --junit path          source file name for junit test result reporting
  --only-changes        only_changes
  --publish             publish
  --quiet               quiet_mode
  --columns DISPLAY_COLUMNS
                        display_columns"""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

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
    supplied_arguments = ["--quiet"]

    expected_return_code = 2
    expected_output = """usage: main.py [-h] [--version] [--cobertura path] [--junit path]
               [--only-changes] [--publish] [--quiet]
               [--columns DISPLAY_COLUMNS]

Summarize Python files.

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --cobertura path      source file name for cobertura test coverage reporting
  --junit path          source file name for junit test result reporting
  --only-changes        only_changes
  --publish             publish
  --quiet               quiet_mode
  --columns DISPLAY_COLUMNS
                        display_columns"""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

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
    supplied_arguments = ["--columns"]

    expected_return_code = 2
    expected_output = ""
    expected_error = """usage: main.py [-h] [--version] [--cobertura path] [--junit path]
               [--only-changes] [--publish] [--quiet]
               [--columns DISPLAY_COLUMNS]
main.py: error: argument --columns: expected one argument"""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

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
    supplied_arguments = ["--columns", "100"]

    expected_return_code = 2
    expected_output = """usage: main.py [-h] [--version] [--cobertura path] [--junit path]
               [--only-changes] [--publish] [--quiet]
               [--columns DISPLAY_COLUMNS]

Summarize Python files.

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --cobertura path      source file name for cobertura test coverage reporting
  --junit path          source file name for junit test result reporting
  --only-changes        only_changes
  --publish             publish
  --quiet               quiet_mode
  --columns DISPLAY_COLUMNS
                        display_columns"""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

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
    supplied_arguments = ["--columns", "20"]

    expected_return_code = 2
    expected_output = ""
    expected_error = """usage: main.py [-h] [--version] [--cobertura path] [--junit path]
               [--only-changes] [--publish] [--quiet]
               [--columns DISPLAY_COLUMNS]
main.py: error: argument --columns: invalid __verify_display_columns value: '20'"""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )

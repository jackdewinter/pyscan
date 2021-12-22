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
    expected_output = """usage: main.py [-h] [--version] [--junit path] [--cobertura path]
               [--only-changes] [--publish]

Summarize Python files.

optional arguments:
  -h, --help        show this help message and exit
  --version         show program's version number and exit
  --junit path      source file for any reporting on test success
  --cobertura path  source file for any reporting on test coverage
  --only-changes    only_changes
  --publish         publish
"""
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
    expected_output = """usage: __main.py__ [-h] [--version] [--junit path] [--cobertura path]
                   [--only-changes] [--publish]

Summarize Python files.

optional arguments:
  -h, --help        show this help message and exit
  --version         show program's version number and exit
  --junit path      source file for any reporting on test success
  --cobertura path  source file for any reporting on test coverage
  --only-changes    only_changes
  --publish         publish
"""
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
    expected_output = """usage: main.py [-h] [--version] [--junit path] [--cobertura path]
               [--only-changes] [--publish]

Summarize Python files.

optional arguments:
  -h, --help        show this help message and exit
  --version         show program's version number and exit
  --junit path      source file for any reporting on test success
  --cobertura path  source file for any reporting on test coverage
  --only-changes    only_changes
  --publish         publish
"""
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
    expected_output = """usage: main.py [-h] [--version] [--junit path] [--cobertura path]
               [--only-changes] [--publish]

Summarize Python files.

optional arguments:
  -h, --help        show this help message and exit
  --version         show program's version number and exit
  --junit path      source file for any reporting on test success
  --cobertura path  source file for any reporting on test coverage
  --only-changes    only_changes
  --publish         publish
"""
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )

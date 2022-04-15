"""
Module to provide tests of the plugins and different failure modes.
"""
import os
import tempfile
from test.test_scenarios import MainlineExecutor

from project_summarizer.plugin_manager.project_summarizer_plugin import (
    ProjectSummarizerPlugin,
)


def test_add_plugin_bad_file_name():
    """
    Test the addition of a plugin with a non-existant file name.
    """

    # Arrange
    executor = MainlineExecutor()
    root_pathname = os.path.abspath(os.path.dirname(__file__))
    plugin_file_name = os.path.join(root_pathname, "not-a-valid-file-name")
    suppplied_arguments = ["--add-plugin", plugin_file_name]

    expected_output = ""
    expected_error = """BadPluginError encountered while loading plugins:
Plugin file '{file}' does not exist.""".replace(
        "{file}", plugin_file_name
    )
    expected_return_code = 1

    # Act
    execute_results = executor.invoke_main(arguments=suppplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_add_plugin_bad_python_file():
    """
    Test the addition of a plugin with a file name that exists but is not a python file.
    """

    # Arrange
    executor = MainlineExecutor()
    root_pathname = os.path.abspath(os.path.dirname(__file__))
    plugin_file_name = os.path.join(
        root_pathname, "../test/resources/plugins/not_a_python_file"
    )
    suppplied_arguments = ["--add-plugin", plugin_file_name]
    assert os.path.exists(plugin_file_name)
    full_plugin_file_name = os.path.abspath(plugin_file_name)

    expected_output = ""
    expected_error = """BadPluginError encountered while loading plugins:
Plugin file named '{file}' cannot be loaded.""".replace(
        "{file}", full_plugin_file_name
    )
    expected_return_code = 1

    # Act
    execute_results = executor.invoke_main(arguments=suppplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_add_plugin_bad_class_name():
    """
    Test the addition of a plugin with a file that does not contain a proper class.
    """

    # Arrange
    executor = MainlineExecutor()
    root_pathname = os.path.abspath(os.path.dirname(__file__))
    plugin_file_name = os.path.join(
        root_pathname, "../test/resources/plugins/misnamed.py"
    )
    assert os.path.exists(plugin_file_name)
    full_plugin_file_name = os.path.abspath(plugin_file_name)
    suppplied_arguments = ["--add-plugin", plugin_file_name]

    expected_output = ""
    expected_error = """BadPluginError encountered while loading plugins:
Plugin file named '{file}' does not contain a class named 'Misnamed'.""".replace(
        "{file}", full_plugin_file_name
    )
    expected_return_code = 1

    # Act
    execute_results = executor.invoke_main(arguments=suppplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_add_plugin_bad_constructor():
    """
    Test the addition of a plugin with a file that does not have a constructor that accepts 0 arguments.
    """

    # Arrange
    executor = MainlineExecutor()
    root_pathname = os.path.abspath(os.path.dirname(__file__))
    plugin_file_name = os.path.join(
        root_pathname, "../test/resources/plugins/bad_constructor.py"
    )
    assert os.path.exists(plugin_file_name)
    full_plugin_file_name = os.path.abspath(plugin_file_name)
    suppplied_arguments = ["--add-plugin", plugin_file_name]

    expected_output = ""
    expected_error = """BadPluginError encountered while loading plugins:
Plugin file named '{file}' threw an exception in the constructor for the class 'BadConstructor'.""".replace(
        "{file}", full_plugin_file_name
    )
    expected_return_code = 1

    # Act
    execute_results = executor.invoke_main(arguments=suppplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_add_plugin_bad_set_context():
    """
    Test the addition of a plugin with a file that has a bad set_context function.
    """

    # Arrange
    executor = MainlineExecutor()
    root_pathname = os.path.abspath(os.path.dirname(__file__))
    plugin_file_name = os.path.join(
        root_pathname, "../test/resources/plugins/bad_set_context.py"
    )
    assert os.path.exists(plugin_file_name)
    suppplied_arguments = ["--add-plugin", plugin_file_name, "--publish"]

    expected_output = ""
    expected_error = """Plugin class 'BadSetContext' had a critical failure: Bad Plugin Error calling set_context."""
    expected_return_code = 1

    # Act
    execute_results = executor.invoke_main(arguments=suppplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_add_plugin_bad_get_output_path():
    """
    Test the addition of a plugin with a file that has a bad get_output_path function.
    """

    # Arrange
    executor = MainlineExecutor()
    root_pathname = os.path.abspath(os.path.dirname(__file__))
    plugin_file_name = os.path.join(
        root_pathname, "../test/resources/plugins/bad_output_path.py"
    )
    assert os.path.exists(plugin_file_name)
    suppplied_arguments = ["--add-plugin", plugin_file_name, "--publish"]

    expected_output = ""
    expected_error = (
        "Plugin class 'BadOutputPath' had a critical failure: "
        + "Bad Plugin Error calling get_output_path."
    )
    expected_return_code = 1

    # Act
    execute_results = executor.invoke_main(arguments=suppplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_add_plugin_bad_add_arguments():
    """
    Test the addition of a plugin with a file that has a bad add_command_line_arguments function.
    """

    # Arrange
    executor = MainlineExecutor()
    root_pathname = os.path.abspath(os.path.dirname(__file__))
    plugin_file_name = os.path.join(
        root_pathname, "../test/resources/plugins/bad_add_arguments.py"
    )
    assert os.path.exists(plugin_file_name)
    suppplied_arguments = ["--add-plugin", plugin_file_name, "--publish"]

    expected_output = ""
    expected_error = (
        "Plugin class 'BadAddArguments' had a critical failure: "
        + "Bad Plugin Error calling add_command_line_arguments."
    )
    expected_return_code = 1

    # Act
    execute_results = executor.invoke_main(arguments=suppplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_add_plugin_bad_generate_report():
    """
    Test the addition of a plugin with a file that has a bad generate_report function.
    """

    # Arrange
    with tempfile.TemporaryDirectory() as temporary_work_directory:
        executor = MainlineExecutor()
        root_pathname = os.path.abspath(os.path.dirname(__file__))
        plugin_file_name = os.path.join(
            root_pathname, "../test/resources/plugins/bad_generate_report.py"
        )
        assert os.path.exists(plugin_file_name)
        suppplied_arguments = [
            "--add-plugin",
            plugin_file_name,
            "--report-dir",
            temporary_work_directory,
            "--bad-generate-report",
            "beta",
        ]

        expected_output = ""
        expected_error = (
            "Plugin class 'BadGenerateReport' had a critical failure: "
            + "Bad Plugin Error calling generate_report."
        )
        expected_return_code = 1

        # Act
        execute_results = executor.invoke_main(arguments=suppplied_arguments)

        # Assert
        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )


def test_add_plugin_bad_get_details():
    """
    Test the addition of a plugin with a file that has a bad get_details function.
    """

    # Arrange
    executor = MainlineExecutor()
    plugin_file_name = os.path.join(
        os.getcwd(), "test/resources/plugins/bad_get_details.py"
    )
    assert os.path.exists(plugin_file_name)
    suppplied_arguments = [
        "--add-plugin",
        plugin_file_name,
    ]

    expected_output = ""
    expected_error = """ BadPluginError encountered while loading plugins:
Plugin class 'BadGetDetails' had a critical failure loading the plugin details."""
    expected_return_code = 1

    # Act
    execute_results = executor.invoke_main(arguments=suppplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_add_plugin_bad_get_details_interface():
    """
    Test the addition of a plugin with a file that has a bad get_details function that returns a bad interface.
    """

    # Arrange
    executor = MainlineExecutor()
    plugin_file_name = os.path.join(
        os.getcwd(), "test/resources/plugins/bad_get_details_interface_version.py"
    )
    assert os.path.exists(plugin_file_name)
    full_plugin_path_name = os.path.abspath(plugin_file_name)
    suppplied_arguments = [
        "--add-plugin",
        plugin_file_name,
    ]

    expected_output = ""
    expected_error = """BadPluginError encountered while loading plugins:
Plugin '{file}' with an interface version ('0') that is not '1'.""".replace(
        "{file}", full_plugin_path_name
    )
    expected_return_code = 1

    # Act
    execute_results = executor.invoke_main(arguments=suppplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_add_plugin_bad_get_details_interface_type():
    """
    Test the addition of a plugin with a file that has a bad get_details function that returns a bad interface type.
    """

    # Arrange
    executor = MainlineExecutor()
    plugin_file_name = os.path.join(
        os.getcwd(), "test/resources/plugins/bad_get_details_interface_version_type.py"
    )
    assert os.path.exists(plugin_file_name)
    suppplied_arguments = [
        "--add-plugin",
        plugin_file_name,
    ]

    expected_output = ""
    expected_error = """BadPluginError encountered while loading plugins:
Plugin class 'BadGetDetailsInterfaceVersionType' returned an improperly typed value for field name 'plugin_interface_version'."""
    expected_return_code = 1

    # Act
    execute_results = executor.invoke_main(arguments=suppplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_add_plugin_bad_get_details_id_type():
    """
    Test the addition of a plugin with a file that has a bad get_details function that returns a bad id type.
    """

    # Arrange
    executor = MainlineExecutor()
    plugin_file_name = os.path.join(
        os.getcwd(), "test/resources/plugins/bad_get_details_id_type.py"
    )
    assert os.path.exists(plugin_file_name)
    suppplied_arguments = [
        "--add-plugin",
        plugin_file_name,
    ]

    expected_output = ""
    expected_error = """BadPluginError encountered while loading plugins:
Plugin class 'BadGetDetailsIdType' returned an improperly typed value for field name 'plugin_id'."""
    expected_return_code = 1

    # Act
    execute_results = executor.invoke_main(arguments=suppplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_add_plugin_bad_get_details_id_empty():
    """
    Test the addition of a plugin with a file that has a bad get_details function that returns a bad id that is empty.
    """

    # Arrange
    executor = MainlineExecutor()
    plugin_file_name = os.path.join(
        os.getcwd(), "test/resources/plugins/bad_get_details_id_empty.py"
    )
    assert os.path.exists(plugin_file_name)
    suppplied_arguments = [
        "--add-plugin",
        plugin_file_name,
    ]

    expected_output = ""
    expected_error = """BadPluginError encountered while loading plugins:
Plugin class 'BadGetDetailsIdEmpty' returned an empty value for field name 'plugin_id'."""
    expected_return_code = 1

    # Act
    execute_results = executor.invoke_main(arguments=suppplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )


def test_add_plugin_good_class():
    """
    Test the addition of a plugin with a file that is just fine but does nothing.
    """

    # Arrange
    executor = MainlineExecutor()
    with tempfile.TemporaryDirectory() as temporary_work_directory:

        root_pathname = os.path.abspath(os.path.dirname(__file__))
        plugin_file_name = os.path.join(
            root_pathname, "../test/resources/plugins/tester_one.py"
        )
        assert os.path.exists(plugin_file_name)
        suppplied_arguments = [
            "--add-plugin",
            plugin_file_name,
            "--report-dir",
            temporary_work_directory,
            "--tester-one",
            "file",
        ]
        expected_report_file_name = os.path.join(
            temporary_work_directory, "tester-one.json"
        )

        expected_output = ""
        expected_error = ""
        expected_return_code = 0

        # Act
        execute_results = executor.invoke_main(arguments=suppplied_arguments)

        # Assert
        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )

        all_lines = None
        with open(
            os.path.abspath(expected_report_file_name),
            "r",
            encoding=ProjectSummarizerPlugin.DEFAULT_FILE_ENCODING,
        ) as data_file:
            all_lines = data_file.readlines()
        assert all_lines
        assert len(all_lines) == 1
        assert all_lines[0] == "The file to report on was: file"

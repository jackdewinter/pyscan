"""
Module to provide functionality to test scripts from within pytest.
"""
import difflib
import io
import os
import sys
import traceback
from abc import ABC, abstractmethod


# pylint: disable=too-few-public-methods
class InProcessResult:
    """
    Class to provide for an encapsulation of the results of an execution.
    """

    def __init__(self, return_code, std_out, std_err):
        self.return_code = return_code
        self.std_out = std_out
        self.std_err = std_err

    @classmethod
    def compare_versus_expected(
        cls, stream_name, actual_stream, expected_text, additional_text=None
    ):
        """
        Do a thorough comparison of the actual stream against the expected text.
        """

        if additional_text:
            assert actual_stream.getvalue().startswith(expected_text), (
                "Block\n---\n"
                + expected_text
                + "\n---\nwas not found at the start of\n---\n"
                + actual_stream.getvalue()
            )

            for next_text_block in additional_text:
                was_found = next_text_block in actual_stream.getvalue()
                diff = difflib.ndiff(
                    next_text_block.splitlines(), actual_stream.getvalue().splitlines()
                )

                diff_values = "\n".join(list(diff))
                print(diff_values, file=sys.stderr)
                if not was_found:
                    assert False, (
                        "Block\n---\n"
                        + next_text_block
                        + "\n---\nwas not found in\n---\n"
                        + actual_stream.getvalue()
                    )
        else:
            if actual_stream.getvalue() != expected_text:
                diff = difflib.ndiff(
                    expected_text.splitlines(), actual_stream.getvalue().splitlines()
                )

                diff_values = "\n".join(list(diff))
                assert False, (
                    stream_name + " not as expected:\n---\n" + diff_values + "\n---\n"
                )

    def assert_stream_contents(
        self, stream_name, actual_stream, expected_stream, additional_error=None
    ):
        """
        Assert that the contents of the given stream are as expected.
        """

        result = None
        try:
            if expected_stream:
                self.compare_versus_expected(
                    stream_name, actual_stream, expected_stream, additional_error
                )
            else:
                assert not actual_stream.getvalue(), (
                    "Expected "
                    + stream_name
                    + " to be empty. Not:\n---\n"
                    + actual_stream.getvalue()
                    + "\n---\n"
                )
        except AssertionError as ex:
            result = ex
        finally:
            actual_stream.close()
        return result

    @classmethod
    def assert_return_code(cls, actual_return_code, expected_return_code):
        """
        Assert that the actual return code is as expected.
        """

        result = None
        try:
            assert actual_return_code == expected_return_code, (
                "Actual error code ("
                + str(actual_return_code)
                + ") and expected error code ("
                + str(expected_return_code)
                + ") differ."
            )
        except AssertionError as ex:
            result = ex
        return result

    def assert_results(
        self, stdout=None, stderr=None, error_code=0, additional_error=None
    ):
        """
        Assert the results are as expected in the "assert" phase.
        """

        stdout_error = self.assert_stream_contents("stdout", self.std_out, stdout)
        stderr_error = self.assert_stream_contents(
            "stderr", self.std_err, stderr, additional_error
        )
        return_code_error = self.assert_return_code(self.return_code, error_code)

        combined_error_msg = ""
        if stdout_error:
            combined_error_msg = combined_error_msg + "\n" + str(stdout_error)
        if stderr_error:
            combined_error_msg = combined_error_msg + "\n" + str(stderr_error)
        if return_code_error:
            combined_error_msg = combined_error_msg + "\n" + str(return_code_error)
        assert not combined_error_msg, (
            "Either stdout, stderr, or the return code was not as expected.\n"
            + combined_error_msg
        )

    @classmethod
    def assert_resultant_file(cls, file_path, expected_contents):
        """
        Assert the contents of a given file against it's expected contents.
        """

        split_expected_contents = expected_contents.split("\n")
        with open(file_path, "r") as infile:
            split_actual_contents = infile.readlines()

        are_different = len(split_expected_contents) != len(split_actual_contents)
        if not are_different:
            index = 0
            while index < len(split_expected_contents):
                are_different = (
                    split_expected_contents[index] != split_actual_contents[index]
                )
                if are_different:
                    break
                index = index + 1

        if are_different:
            diff = difflib.ndiff(split_actual_contents, split_expected_contents)
            diff_values = "\n".join(list(diff))
            assert False, (
                "Actual and expected contents of '"
                + file_path
                + "' are not equal:\n---\n"
                + diff_values
                + "\n---\n"
            )


# pylint: enable=too-few-public-methods

# pylint: disable=too-few-public-methods
class SystemState:
    """
    Class to provide an encapsulation of the system state so that we can restore
    it later.
    """

    def __init__(self):
        """
        Initializes a new instance of the SystemState class.
        """

        self.saved_stdout = sys.stdout
        self.saved_stderr = sys.stderr
        self.saved_cwd = os.getcwd()
        self.saved_env = os.environ
        self.saved_argv = sys.argv

    def restore(self):
        """
        Restore the system state variables to what they were before.
        """

        os.chdir(self.saved_cwd)
        os.environ = self.saved_env
        sys.argv = self.saved_argv
        sys.stdout = self.saved_stdout
        sys.stderr = self.saved_stderr


# pylint: enable=too-few-public-methods


class InProcessExecution(ABC):
    """
    Handle the in-process execution of the script's mainline.
    """

    @abstractmethod
    def execute_main(self):
        """
        Provides the code to execute the mainline.  Should be simple like:
        MyObjectClass().main()
        """

    @abstractmethod
    def get_main_name(self):
        """
        Provides the main name to associate with the mainline.  Gets set as
        the first argument to the program.
        """

    @classmethod
    def handle_system_exit(cls, exit_exception, std_error):
        """
        Handle the processing of an "early" exit as a result of our execution.
        """
        returncode = exit_exception.code
        if isinstance(returncode, str):
            std_error.write("{}\n".format(exit_exception))
            returncode = 1
        elif returncode is None:
            returncode = 0
        return returncode

    @classmethod
    def handle_normal_exception(cls):
        """
        Handle the processing of a normal exception as a result of our execution.
        """
        try:
            exception_type, exception_value, trace_back = sys.exc_info()
            traceback.print_exception(
                exception_type, exception_value, trace_back.tb_next
            )
        finally:
            del trace_back
        return 1

    # pylint: disable=broad-except
    def invoke_main(self, arguments=None, cwd=None):
        """
        Invoke the mainline so that we can capture results.
        """

        saved_state = SystemState()

        try:
            returncode = 0

            std_output = io.StringIO()
            std_error = io.StringIO()
            sys.stdout = std_output
            sys.stderr = std_error

            if arguments:
                sys.argv = arguments.copy()
            else:
                sys.argv = []
            sys.argv.insert(0, self.get_main_name())

            if cwd:
                os.chdir(cwd)

            self.execute_main()
        except SystemExit as this_exception:
            returncode = self.handle_system_exit(this_exception, std_error)
        except Exception:
            returncode = self.handle_normal_exception()
        finally:
            saved_state.restore()

        return InProcessResult(returncode, std_output, std_error)

    # pylint: enable=broad-except

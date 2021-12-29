"""
Module to provide for a simple summarization of relevant output files from a build.
"""
import argparse
import os
import runpy
import sys
from shutil import copyfile

from pyscan.cobertura_plugin import CoberturaPlugin
from pyscan.junit_plugin import JUnitPlugin
from pyscan.pyscan_plugin import PyScanPlugin


class PyScan:
    """
    Class to provide for a simple summarization of relevant output files from a build.
    """

    def __init__(self):
        self.__version_number = PyScan.__get_semantic_version()
        self.test_summary_publish_path = PyScanPlugin.SUMMARY_PUBLISH_PATH
        self.debug = False
        self.__available_plugins = None
        self.__plugin_argument_names = {}
        self.__plugin_variable_names = {}

    @staticmethod
    def __get_semantic_version():
        file_path = __file__
        assert os.path.isabs(file_path)
        file_path = file_path.replace(os.sep, "/")
        last_index = file_path.rindex("/")
        file_path = file_path[: last_index + 1] + "version.py"
        version_meta = runpy.run_path(file_path)
        return version_meta["__version__"]

    def __parse_arguments(self):
        """
        Handle any arguments for the program.
        """

        parser = argparse.ArgumentParser(
            description="Summarize Python files.", allow_abbrev=False
        )

        parser.add_argument(
            "--version",
            action="version",
            version="%(prog)s " + self.__version_number,
        )

        for next_plugin_instance in self.__available_plugins:
            (
                plugin_argument_name,
                plugin_variable_name,
            ) = next_plugin_instance.add_command_line_arguments(parser)
            self.__plugin_argument_names[plugin_argument_name] = next_plugin_instance
            self.__plugin_variable_names[plugin_argument_name] = plugin_variable_name

        parser.add_argument(
            "--only-changes",
            dest="only_changes",
            action="store_true",
            default=False,
            help="only_changes",
        )
        parser.add_argument(
            "--publish",
            dest="publish_summaries",
            action="store_true",
            default=False,
            help="publish",
        )

        args = parser.parse_args()
        if not args.publish_summaries and not args.test_report_file:
            are_plugin_arguments_present = False
            arguments_as_dictionary = vars(args)
            for next_plugin_argument in self.__plugin_argument_names:
                plugin_variable_name = self.__plugin_variable_names[
                    next_plugin_argument
                ]
                assert plugin_variable_name in arguments_as_dictionary
                argument_value = arguments_as_dictionary[plugin_variable_name]
                are_plugin_arguments_present = bool(argument_value.strip())
                if are_plugin_arguments_present:
                    break

            if not are_plugin_arguments_present:
                parser.print_help()
                sys.exit(2)
        return args

    def __publish_file(self, file_to_publish):
        """
        Publish the specified file to the set publish directory.
        """

        if not os.path.exists(self.test_summary_publish_path):
            print(
                f"Publish directory '{self.test_summary_publish_path}' does not exist.  Creating."
            )
            os.makedirs(self.test_summary_publish_path)
        elif not os.path.isdir(self.test_summary_publish_path):
            print(
                f"Publish directory '{self.test_summary_publish_path}' already exists, but as a file."
            )
            sys.exit(1)

        if os.path.exists(file_to_publish):
            try:
                copyfile(
                    file_to_publish,
                    PyScanPlugin.compute_published_path_to_file(file_to_publish),
                )
            except IOError as ex:
                print(f"Publishing file '{file_to_publish}' failed ({ex}).")
                sys.exit(1)

    def publish_summaries(self):
        """
        Respond to a request to publish any existing summaries.
        """

        valid_paths = []
        for plugin_instance in self.__available_plugins:
            plugin_output_path = plugin_instance.get_output_path()

            if os.path.exists(plugin_output_path) and not os.path.isfile(
                plugin_output_path
            ):
                print(f"Summary path '{plugin_output_path}' is not a file.")
                sys.exit(1)
            valid_paths.append(plugin_output_path)

        for plugin_output_path in valid_paths:
            self.__publish_file(plugin_output_path)

    def main(self):
        """
        Main entrance point.
        """
        self.__available_plugins = [CoberturaPlugin(), JUnitPlugin()]

        args = self.__parse_arguments()

        if args.publish_summaries:
            self.publish_summaries()
            sys.exit(0)

        arguments_as_dictionary = vars(args)
        for next_command_line_argument in sys.argv:
            if next_command_line_argument in self.__plugin_argument_names:
                plugin_instance = self.__plugin_argument_names[
                    next_command_line_argument
                ]
                plugin_variable_name = self.__plugin_variable_names[
                    next_command_line_argument
                ]
                plugin_instance.generate_report(
                    args.only_changes, arguments_as_dictionary[plugin_variable_name]
                )


if __name__ == "__main__":
    PyScan().main()

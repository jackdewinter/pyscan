"""
Module to provide for a simple summarization of relevant output files from a build.
"""
import argparse
import os
import runpy
import sys
from shutil import copyfile

from project_summarizer.cobertura_plugin import CoberturaPlugin
from project_summarizer.junit_plugin import JUnitPlugin
from project_summarizer.project_summarizer_plugin import ProjectSummarizerPlugin


# pylint: disable=too-few-public-methods
class ProjectSummarizer:
    """
    Class to provide for a simple summarization of relevant output files from a build.
    """

    __MINIMUM_DISPLAY_COLUMNS = 50
    __MAXIMUM_DISPLAY_COLUMNS = 200

    def __init__(self):
        self.__version_number = ProjectSummarizer.__get_semantic_version()
        self.test_summary_publish_path = ProjectSummarizerPlugin.SUMMARY_PUBLISH_PATH
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
        file_path = f"{file_path[: last_index + 1]}version.py"
        version_meta = runpy.run_path(file_path)
        return version_meta["__version__"]

    def __add_command_line_arguments_for_plugins(self, parser):
        for next_plugin_instance in self.__available_plugins:
            (
                plugin_argument_name,
                plugin_variable_name,
            ) = next_plugin_instance.add_command_line_arguments(parser)
            self.__plugin_argument_names[plugin_argument_name] = next_plugin_instance
            self.__plugin_variable_names[plugin_argument_name] = plugin_variable_name

    def __show_help_if_no_meaningful_arguments_found(self, args, parser):
        if args.publish_summaries:
            return

        are_plugin_arguments_present = False
        arguments_as_dictionary = vars(args)
        for next_plugin_argument in self.__plugin_argument_names:
            plugin_variable_name = self.__plugin_variable_names[next_plugin_argument]
            assert plugin_variable_name in arguments_as_dictionary
            argument_value = arguments_as_dictionary[plugin_variable_name]
            are_plugin_arguments_present = bool(argument_value.strip())
            if are_plugin_arguments_present:
                break

        if not are_plugin_arguments_present:
            parser.print_help()
            sys.exit(2)

    def __parse_arguments(self):
        parser = argparse.ArgumentParser(
            description="Summarize Python files.", allow_abbrev=False
        )

        parser.add_argument(
            "--version",
            action="version",
            version=f"%(prog)s {self.__version_number}",
        )
        self.__add_command_line_arguments_for_plugins(parser)
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
        parser.add_argument(
            "--quiet",
            dest="quiet_mode",
            action="store_true",
            default=False,
            help="quiet_mode",
        )
        parser.add_argument(
            "--columns",
            dest="display_columns",
            action="store",
            default=-1,
            help="display_columns",
            type=ProjectSummarizer.__verify_display_columns,
        )

        args = parser.parse_args()
        self.__show_help_if_no_meaningful_arguments_found(args, parser)
        return args

    @staticmethod
    def __verify_display_columns(argument):
        argument_as_integer = int(argument)
        if (
            argument_as_integer < ProjectSummarizer.__MINIMUM_DISPLAY_COLUMNS
            or argument_as_integer > ProjectSummarizer.__MAXIMUM_DISPLAY_COLUMNS
        ):
            raise ValueError(
                f"Value '{argument}' is not an integer between "
                + f"between {ProjectSummarizer.__MINIMUM_DISPLAY_COLUMNS} "
                + f"and {ProjectSummarizer.__MAXIMUM_DISPLAY_COLUMNS}."
            )
        return argument_as_integer

    def __publish_file(self, file_to_publish):
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
                    ProjectSummarizerPlugin.compute_published_path_to_file(
                        file_to_publish
                    ),
                )
            except IOError as ex:
                print(f"Publishing file '{file_to_publish}' failed ({ex}).")
                sys.exit(1)

    def __publish_summaries(self):
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

    def __create_summaries(self, args):
        arguments_as_dictionary = vars(args)
        column_width = 0 if args.quiet_mode else args.display_columns
        for next_command_line_argument in sys.argv:
            if next_command_line_argument in self.__plugin_argument_names:
                plugin_instance = self.__plugin_argument_names[
                    next_command_line_argument
                ]
                plugin_variable_name = self.__plugin_variable_names[
                    next_command_line_argument
                ]
                plugin_instance.generate_report(
                    args.only_changes,
                    column_width,
                    arguments_as_dictionary[plugin_variable_name],
                )

    def main(self):
        """
        Main entrance point.
        """
        self.__available_plugins = [CoberturaPlugin(), JUnitPlugin()]

        args = self.__parse_arguments()

        if args.publish_summaries:
            self.__publish_summaries()
            sys.exit(0)

        self.__create_summaries(args)


if __name__ == "__main__":
    ProjectSummarizer().main()
# pylint: enable=too-few-public-methods

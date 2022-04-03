"""
Module to provide for a simple summarization of relevant output files from a build.
"""
import argparse
import os
import runpy
import sys
from shutil import copyfile
from typing import Dict, List

from project_summarizer.cobertura_plugin import CoberturaPlugin
from project_summarizer.junit_plugin import JUnitPlugin
from project_summarizer.project_summarizer_plugin import ProjectSummarizerPlugin
from project_summarizer.summarize_context import SummarizeContext


# pylint: disable=too-few-public-methods
class ProjectSummarizer:
    """
    Class to provide for a simple summarization of relevant output files from a build.
    """

    __MINIMUM_DISPLAY_COLUMNS = 50
    __MAXIMUM_DISPLAY_COLUMNS = 200

    def __init__(self) -> None:
        self.__version_number: str = ProjectSummarizer.__get_semantic_version()
        self.debug: bool = False
        self.__available_plugins: List[ProjectSummarizerPlugin] = []
        self.__plugin_argument_names: Dict[str, ProjectSummarizerPlugin] = {}
        self.__plugin_variable_names: Dict[str, str] = {}

    @staticmethod
    def __get_semantic_version() -> str:
        file_path = __file__
        assert os.path.isabs(file_path)
        file_path = file_path.replace(os.sep, "/")
        last_index = file_path.rindex("/")
        file_path = f"{file_path[: last_index + 1]}version.py"
        version_meta = runpy.run_path(file_path)
        return str(version_meta["__version__"])

    def __add_command_line_arguments_for_plugins(
        self, parser: argparse.ArgumentParser
    ) -> None:
        for next_plugin_instance in self.__available_plugins:
            (
                plugin_argument_name,
                plugin_variable_name,
            ) = next_plugin_instance.add_command_line_arguments(parser)
            self.__plugin_argument_names[plugin_argument_name] = next_plugin_instance
            self.__plugin_variable_names[plugin_argument_name] = plugin_variable_name

    def __show_help_if_no_meaningful_arguments_found(
        self, args: argparse.Namespace, parser: argparse.ArgumentParser
    ) -> None:
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
            print(
                "Error: Either --publish or one of the reporting arguments mush be specified."
            )
            parser.print_help()
            sys.exit(2)

    def __parse_arguments(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description="Summarize Python files.", allow_abbrev=False, add_help=False
        )
        parser.add_argument(
            "-h", "--help", action="help", help="Show this help message and exit."
        )
        parser.add_argument(
            "--version",
            action="version",
            version=f"%(prog)s {self.__version_number}",
            help="Show program's version number and exit.",
        )
        parser.add_argument(
            "--report-dir",
            dest="report_dir",
            action="store",
            default="report",
            help="Directory to generate the summary reports in.",
            type=ProjectSummarizer.__verify_directory_exists,
        )
        parser.add_argument(
            "--publish-dir",
            dest="publish_dir",
            action="store",
            default=None,
            help="Directory to publish the summary reports to.",
            type=ProjectSummarizer.__verify_directory_exists,
        )

        self.__add_command_line_arguments_for_plugins(parser)

        parser.add_argument(
            "--only-changes",
            dest="only_changes",
            action="store_true",
            default=False,
            help="Only the summary items that have changed are displayed in the console summary.",
        )
        parser.add_argument(
            "--publish",
            dest="publish_summaries",
            action="store_true",
            default=False,
            help="Publish the summaries to the publish directory and exit.",
        )
        parser.add_argument(
            "--quiet",
            dest="quiet_mode",
            action="store_true",
            default=False,
            help="The report summary files will be generated, but no summary will be output to the console.",
        )
        parser.add_argument(
            "--columns",
            dest="display_columns",
            action="store",
            default=-1,
            help="Specifies the number of character columns to use in the console summary.",
            type=ProjectSummarizer.__verify_display_columns,
        )

        args = parser.parse_args()
        self.__show_help_if_no_meaningful_arguments_found(args, parser)
        return args

    @staticmethod
    def __verify_display_columns(argument: str) -> int:
        argument_as_integer = int(argument)
        if (
            argument_as_integer < ProjectSummarizer.__MINIMUM_DISPLAY_COLUMNS
            or argument_as_integer > ProjectSummarizer.__MAXIMUM_DISPLAY_COLUMNS
        ):
            raise argparse.ArgumentTypeError(
                f"Value '{argument}' is not an integer between "
                + f"between {ProjectSummarizer.__MINIMUM_DISPLAY_COLUMNS} "
                + f"and {ProjectSummarizer.__MAXIMUM_DISPLAY_COLUMNS}."
            )
        return argument_as_integer

    @staticmethod
    def __verify_directory_exists(argument: str) -> str:
        report_argument = argument.replace("\\\\", "\\")
        if not os.path.exists(argument):
            raise argparse.ArgumentTypeError(
                f"Path '{report_argument}' does not exist."
            )
        if not os.path.isdir(argument):
            raise argparse.ArgumentTypeError(
                f"Path '{report_argument}' is not an existing directory."
            )
        return argument

    @classmethod
    def __publish_file(cls, file_to_publish: str, context: SummarizeContext) -> None:
        if os.path.exists(file_to_publish):
            try:
                publish_path = context.compute_published_path_to_file(file_to_publish)
                copyfile(
                    file_to_publish,
                    publish_path,
                )
                print(f"Published: {publish_path}")
            except IOError as ex:
                print(f"Publishing file '{file_to_publish}' failed ({ex}).")
                sys.exit(1)

    def __publish_summaries(self, context: SummarizeContext) -> None:
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

        if not os.path.exists(context.publish_dir):
            print(
                f"Publish directory '{context.publish_dir}' does not exist.  Creating."
            )
            os.makedirs(context.publish_dir)
        elif not os.path.isdir(context.publish_dir):
            print(
                f"Publish directory '{context.publish_dir}' already exists, but as a file."
            )
            sys.exit(1)

        for plugin_output_path in valid_paths:
            self.__publish_file(plugin_output_path, context)

    def __create_summaries(self, args: argparse.Namespace) -> None:
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

    def main(self) -> None:
        """
        Main entrance point.
        """
        self.__available_plugins = [CoberturaPlugin(), JUnitPlugin()]

        args = self.__parse_arguments()

        context = SummarizeContext(
            report_dir=args.report_dir
            or ProjectSummarizerPlugin.DEFAULT_REPORT_PUBLISH_PATH,
            publish_dir=args.publish_dir
            or ProjectSummarizerPlugin.DEFAULT_SUMMARY_PUBLISH_PATH,
        )

        for next_plugin in self.__available_plugins:
            next_plugin.set_context(context)
        # report_dir

        if args.publish_summaries:
            self.__publish_summaries(context)
            sys.exit(0)

        self.__create_summaries(args)
        sys.exit(0)


if __name__ == "__main__":
    ProjectSummarizer().main()

# pylint: enable=too-few-public-methods

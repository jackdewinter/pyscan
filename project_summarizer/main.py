"""
Module to provide for a simple summarization of relevant output files from a build.
"""

import argparse
import os
import runpy
import sys
import traceback
from shutil import copyfile
from typing import List

from project_summarizer.plugin_manager.bad_plugin_error import BadPluginError
from project_summarizer.plugin_manager.plugin_manager import PluginManager
from project_summarizer.plugin_manager.project_summarizer_plugin import (
    ProjectSummarizerPlugin,
)
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
        self.__plugin_manager = PluginManager()
        self.__show_stack_trace = False

    @staticmethod
    def __get_semantic_version() -> str:
        file_path = __file__
        assert os.path.isabs(file_path)
        file_path = file_path.replace(os.sep, "/")
        last_index = file_path.rindex("/")
        file_path = f"{file_path[: last_index + 1]}version.py"
        version_meta = runpy.run_path(file_path)
        return str(version_meta["__version__"])

    def __show_help_if_no_meaningful_arguments_found(
        self, args: argparse.Namespace, parser: argparse.ArgumentParser
    ) -> None:
        if args.publish_summaries:
            return

        are_plugin_arguments_present = self.__plugin_manager.find_any_plugins_arguments(
            args
        )
        if not are_plugin_arguments_present:
            print(
                "Error: Either --publish or one of the reporting arguments mush be specified."
            )
            parser.print_help()
            sys.exit(2)

    def __parse_arguments(self, unused_arguments: List[str]) -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description="Summarize Python files.", allow_abbrev=False, add_help=False
        )
        parser.add_argument(
            "-h", "--help", action="help", help="Show this help message and exit."
        )
        parser.add_argument(
            "--version",
            action="version",
            version=f"{self.__version_number}",
            help="Show program's version number and exit.",
        )
        parser.add_argument(
            "--stack-trace",
            dest="show_stack_trace",
            action="store_true",
            default=False,
            help="if an error occurs, print out the stack trace for debug purposes",
        )

        PluginManager.add_plugin_arguments(parser)
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

        self.__plugin_manager.add_command_line_arguments_for_plugins(parser)

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

        args = parser.parse_args(args=unused_arguments)
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

        valid_paths = self.__plugin_manager.get_output_paths()

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
            self.__plugin_manager.generate_report(
                next_command_line_argument, arguments_as_dictionary, column_width, args
            )

    def __report_error(
        self, error_to_report: BadPluginError, is_loading: bool = False
    ) -> None:
        if is_loading:
            print("BadPluginError encountered while loading plugins:", file=sys.stderr)
        print(error_to_report, file=sys.stderr)
        if self.__show_stack_trace:
            traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    def __initialize_plugins(self) -> List[str]:
        try:
            return self.__plugin_manager.initialize_plugins()
        except BadPluginError as this_exception:
            self.__report_error(this_exception, True)
            return []  # pragma: no cover

    def main(self) -> None:
        """
        Main entrance point.
        """
        try:
            remaining_arguments = self.__initialize_plugins()
            args = self.__parse_arguments(remaining_arguments)
            self.__show_stack_trace = args.show_stack_trace

            context = SummarizeContext(
                report_dir=args.report_dir
                or ProjectSummarizerPlugin.DEFAULT_REPORT_PUBLISH_PATH,
                publish_dir=args.publish_dir
                or ProjectSummarizerPlugin.DEFAULT_SUMMARY_PUBLISH_PATH,
            )

            self.__plugin_manager.set_context(context)

            if args.publish_summaries:
                self.__publish_summaries(context)
            else:
                self.__create_summaries(args)
            sys.exit(0)
        except BadPluginError as this_exception:
            self.__report_error(this_exception)


if __name__ == "__main__":
    ProjectSummarizer().main()

# pylint: enable=too-few-public-methods

import argparse
from typing import Tuple

from project_summarizer.plugin_manager.plugin_details import PluginDetails
from project_summarizer.plugin_manager.project_summarizer_plugin import (
    ProjectSummarizerPlugin,
)
from project_summarizer.summarize_context import SummarizeContext


class BadGetDetails(ProjectSummarizerPlugin):
    """
    Class to implement a sample plugin that has a bad get_details function, but everything else is okay.
    """

    __COMMAND_LINE_ARGUMENT = "--output_path"
    __COMMAND_LINE_OPTION = "output_path_file"

    def get_details(self) -> PluginDetails:
        """
        Get the details for the plugin.
        """
        raise Exception("get_details")  # sourcery skip: raise-specific-error

    def set_context(self, context: SummarizeContext) -> None:
        """
        Set the context for the plugins.
        """
        _ = context

    def get_output_path(self) -> str:
        """
        Get the output path for the reporting file.
        """
        return ".."

    def add_command_line_arguments(
        self, parser: argparse.ArgumentParser
    ) -> Tuple[str, str]:
        """
        Add a command line argument to denote the file to scan.
        """
        parser.add_argument(
            BadGetDetails.__COMMAND_LINE_ARGUMENT,
            dest=BadGetDetails.__COMMAND_LINE_OPTION,
            metavar="path",
            action="store",
            default="",
            help="Source file name for cobertura test coverage reporting.",
        )
        return (
            BadGetDetails.__COMMAND_LINE_ARGUMENT,
            BadGetDetails.__COMMAND_LINE_OPTION,
        )

    def generate_report(
        self, only_changes: bool, column_width: int, report_file: str
    ) -> None:
        """
        Generate the report and display it.
        """
        pass

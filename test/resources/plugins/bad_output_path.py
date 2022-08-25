import argparse
from typing import Tuple

from project_summarizer.plugin_manager.plugin_details import PluginDetails
from project_summarizer.plugin_manager.project_summarizer_plugin import (
    ProjectSummarizerPlugin,
)
from project_summarizer.summarize_context import SummarizeContext


class BadOutputPath(ProjectSummarizerPlugin):
    """
    Class to implement a sample plugin that has a bad get_output_path function, but everything else is okay.
    """

    __COMMAND_LINE_ARGUMENT = "--output_path"
    __COMMAND_LINE_OPTION = "output_path_file"

    __PLUGIN_ID = "BOP"
    __PLUGIN_NAME = "Bad Output Path Results"
    __PLUGIN_VERSION = "0.5.0"

    def get_details(self) -> PluginDetails:
        """
        Get the details for the plugin.
        """
        return PluginDetails(
            BadOutputPath.__PLUGIN_ID,
            BadOutputPath.__PLUGIN_NAME,
            BadOutputPath.__PLUGIN_VERSION,
            ProjectSummarizerPlugin.VERSION_BASIC,
        )

    def set_context(self, context: SummarizeContext) -> None:
        """
        Set the context for the plugins.
        """
        _ = context

    def get_output_path(self) -> str:
        """
        Get the output path for the reporting file.
        """
        raise Exception("bad_get_output_path")  # sourcery skip: raise-specific-error

    def add_command_line_arguments(
        self, parser: argparse.ArgumentParser
    ) -> Tuple[str, str]:
        """
        Add a command line argument to denote the file to scan.
        """
        parser.add_argument(
            BadOutputPath.__COMMAND_LINE_ARGUMENT,
            dest=BadOutputPath.__COMMAND_LINE_OPTION,
            metavar="path",
            action="store",
            default="",
            help="Source file name for cobertura test coverage reporting.",
        )
        return (
            BadOutputPath.__COMMAND_LINE_ARGUMENT,
            BadOutputPath.__COMMAND_LINE_OPTION,
        )

    def generate_report(
        self, only_changes: bool, column_width: int, report_file: str
    ) -> None:
        """
        Generate the report and display it.
        """
        pass

import argparse
from typing import Tuple

from project_summarizer.plugin_manager.plugin_details import PluginDetails
from project_summarizer.plugin_manager.project_summarizer_plugin import (
    ProjectSummarizerPlugin,
)
from project_summarizer.summarize_context import SummarizeContext


class BadSetContext(ProjectSummarizerPlugin):
    """
    Class to implement a sample plugin that has a bad set_context function, but everything else is okay.
    """

    __COMMAND_LINE_ARGUMENT = "--set-context"
    __COMMAND_LINE_OPTION = "set_context_file"

    __PLUGIN_ID = "BSC"
    __PLUGIN_NAME = "Bad Set Context Results"
    __PLUGIN_VERSION = "0.5.0"

    def __init__(self) -> None:
        super().__init__()
        self.__output_path: str = ""

    def get_details(self) -> PluginDetails:
        """
        Get the details for the plugin.
        """
        return PluginDetails(
            BadSetContext.__PLUGIN_ID,
            BadSetContext.__PLUGIN_NAME,
            BadSetContext.__PLUGIN_VERSION,
            ProjectSummarizerPlugin.VERSION_BASIC,
        )

    def set_context(self, context: SummarizeContext) -> None:
        """
        Set the context for the plugins.
        """
        raise Exception("bad_set_context")  # sourcery skip: raise-specific-error

    def get_output_path(self) -> str:
        """
        Get the output path for the reporting file.
        """
        return self.__output_path

    def add_command_line_arguments(
        self, parser: argparse.ArgumentParser
    ) -> Tuple[str, str]:
        """
        Add a command line argument to denote the file to scan.
        """
        parser.add_argument(
            BadSetContext.__COMMAND_LINE_ARGUMENT,
            dest=BadSetContext.__COMMAND_LINE_OPTION,
            metavar="path",
            action="store",
            default="",
            help="Source file name for cobertura test coverage reporting.",
        )
        return (
            BadSetContext.__COMMAND_LINE_ARGUMENT,
            BadSetContext.__COMMAND_LINE_OPTION,
        )

    def generate_report(
        self, only_changes: bool, column_width: int, report_file: str
    ) -> None:
        """
        Generate the report and display it.
        """
        pass

import argparse
import os
from typing import Optional, Tuple

from project_summarizer.plugin_manager.plugin_details import PluginDetails
from project_summarizer.plugin_manager.project_summarizer_plugin import (
    ProjectSummarizerPlugin,
)
from project_summarizer.summarize_context import SummarizeContext


class BadGenerateReport(ProjectSummarizerPlugin):
    """
    Class to implement a sample plugin that has a bad generate_report function, but everything else is okay.
    """

    __COMMAND_LINE_ARGUMENT = "--bad-generate-report"
    __COMMAND_LINE_OPTION = "bad_generate_report_file"

    __PLUGIN_ID = "BGR"
    __PLUGIN_NAME = "Bad Gen Report Results"
    __PLUGIN_VERSION = "0.5.0"

    def __init__(self) -> None:
        super().__init__()
        self.__output_path: str = ""
        self.__context: Optional[SummarizeContext] = None

    def get_details(self) -> PluginDetails:
        """
        Get the details for the plugin.
        """
        return PluginDetails(
            BadGenerateReport.__PLUGIN_ID,
            BadGenerateReport.__PLUGIN_NAME,
            BadGenerateReport.__PLUGIN_VERSION,
            ProjectSummarizerPlugin.VERSION_BASIC,
        )

    def set_context(self, context: SummarizeContext) -> None:
        """
        Set the context for the plugins.
        """
        self.__context = context
        self.__output_path = os.path.join(self.__context.report_dir, "coverage.json")

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
            BadGenerateReport.__COMMAND_LINE_ARGUMENT,
            dest=BadGenerateReport.__COMMAND_LINE_OPTION,
            metavar="path",
            action="store",
            default="",
            help="Source file name for cobertura test coverage reporting.",
        )
        return (
            BadGenerateReport.__COMMAND_LINE_ARGUMENT,
            BadGenerateReport.__COMMAND_LINE_OPTION,
        )

    def generate_report(
        self, only_changes: bool, column_width: int, report_file: str
    ) -> None:
        """
        Generate the report and display it.
        """
        raise Exception("generate_report")  # sourcery skip: raise-specific-error

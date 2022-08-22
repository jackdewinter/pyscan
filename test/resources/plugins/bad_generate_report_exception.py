import argparse
import os
from typing import Optional, Tuple

from project_summarizer.plugin_manager.bad_plugin_error import BadPluginError
from project_summarizer.plugin_manager.plugin_details import PluginDetails
from project_summarizer.plugin_manager.project_summarizer_plugin import (
    ProjectSummarizerPlugin,
)
from project_summarizer.summarize_context import SummarizeContext


class BadGenerateReportException(ProjectSummarizerPlugin):
    """
    Class to implement a sample plugin that has a bad generate_report function
    that throws a BadPluginError, but everything else is okay.
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
            BadGenerateReportException.__PLUGIN_ID,
            BadGenerateReportException.__PLUGIN_NAME,
            BadGenerateReportException.__PLUGIN_VERSION,
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
            BadGenerateReportException.__COMMAND_LINE_ARGUMENT,
            dest=BadGenerateReportException.__COMMAND_LINE_OPTION,
            metavar="path",
            action="store",
            default="",
            help="Source file name for cobertura test coverage reporting.",
        )
        return (
            BadGenerateReportException.__COMMAND_LINE_ARGUMENT,
            BadGenerateReportException.__COMMAND_LINE_OPTION,
        )

    def generate_report(
        self, only_changes: bool, column_width: int, report_file: str
    ) -> None:
        """
        Generate the report and display it.
        """
        raise BadPluginError(formatted_message="bad_generate_report")

import argparse
from typing import Tuple

from project_summarizer.plugin_manager.plugin_details import PluginDetails
from project_summarizer.plugin_manager.project_summarizer_plugin import (
    ProjectSummarizerPlugin,
)
from project_summarizer.summarize_context import SummarizeContext


class BadGetDetailsInterfaceVersionType(ProjectSummarizerPlugin):
    """
    Class to implement a sample plugin that returns a bad interface version type, but everything else is okay.
    """

    __COMMAND_LINE_ARGUMENT = "--bad_get_details_interface_path_type"
    __COMMAND_LINE_OPTION = "bad_get_details_interface_type_file"

    __PLUGIN_ID = "TEST1"
    __PLUGIN_NAME = "Tester One Results"
    __PLUGIN_VERSION = "0.5.0"

    def get_details(self) -> PluginDetails:
        """
        Get the details for the plugin.
        """
        return PluginDetails(
            BadGetDetailsInterfaceVersionType.__PLUGIN_ID,
            BadGetDetailsInterfaceVersionType.__PLUGIN_NAME,
            BadGetDetailsInterfaceVersionType.__PLUGIN_VERSION,
            "Word",
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
        return ".."

    def add_command_line_arguments(
        self, parser: argparse.ArgumentParser
    ) -> Tuple[str, str]:
        """
        Add a command line argument to denote the file to scan.
        """
        parser.add_argument(
            BadGetDetailsInterfaceVersionType.__COMMAND_LINE_ARGUMENT,
            dest=BadGetDetailsInterfaceVersionType.__COMMAND_LINE_OPTION,
            metavar="path",
            action="store",
            default="",
            help="Source file name for cobertura test coverage reporting.",
        )
        return (
            BadGetDetailsInterfaceVersionType.__COMMAND_LINE_ARGUMENT,
            BadGetDetailsInterfaceVersionType.__COMMAND_LINE_OPTION,
        )

    def generate_report(
        self, only_changes: bool, column_width: int, report_file: str
    ) -> None:
        """
        Generate the report and display it.
        """
        pass

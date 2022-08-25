import argparse
import os
from typing import Optional, Tuple

from project_summarizer.plugin_manager.plugin_details import PluginDetails
from project_summarizer.plugin_manager.project_summarizer_plugin import (
    ProjectSummarizerPlugin,
)
from project_summarizer.summarize_context import SummarizeContext


class BadAddArguments(ProjectSummarizerPlugin):
    """
    Class to implement a sample plugin that has a bad add_command_line_arguments function, but everything else is okay.
    """

    __COMMAND_LINE_ARGUMENT = "--add_command_line_arguments"
    __COMMAND_LINE_OPTION = "add_command_line_arguments_file"

    __PLUGIN_ID = "BSC"
    __PLUGIN_NAME = "Bad Set Context Results"
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
            BadAddArguments.__PLUGIN_ID,
            BadAddArguments.__PLUGIN_NAME,
            BadAddArguments.__PLUGIN_VERSION,
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
        raise Exception("bad_add_arguments")  # sourcery skip: raise-specific-error

    def generate_report(
        self, only_changes: bool, column_width: int, report_file: str
    ) -> None:
        """
        Generate the report and display it.
        """
        pass

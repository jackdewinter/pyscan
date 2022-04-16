import argparse
import os
from typing import Optional, Tuple

from project_summarizer.plugin_manager.plugin_details import PluginDetails
from project_summarizer.plugin_manager.project_summarizer_plugin import (
    ProjectSummarizerPlugin,
)
from project_summarizer.summarize_context import SummarizeContext


class TesterOne(ProjectSummarizerPlugin):
    """
    Class to implement a sample plugin that...
    """

    __COMMAND_LINE_ARGUMENT = "--tester-one"
    __COMMAND_LINE_OPTION = "tester_one_file"

    __PLUGIN_ID = "TEST1"
    __PLUGIN_NAME = "Tester One Results"
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
            TesterOne.__PLUGIN_ID,
            TesterOne.__PLUGIN_NAME,
            TesterOne.__PLUGIN_VERSION,
            ProjectSummarizerPlugin.VERSION_BASIC,
        )

    def set_context(self, context: SummarizeContext) -> None:
        """
        Set the context for the plugins.
        """
        self.__context = context
        self.__output_path = os.path.join(self.__context.report_dir, "tester-one.json")

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
            TesterOne.__COMMAND_LINE_ARGUMENT,
            dest=TesterOne.__COMMAND_LINE_OPTION,
            metavar="path",
            action="store",
            default="",
            help="Source file name for cobertura test coverage reporting.",
        )
        return (
            TesterOne.__COMMAND_LINE_ARGUMENT,
            TesterOne.__COMMAND_LINE_OPTION,
        )

    def generate_report(
        self, only_changes: bool, column_width: int, report_file: str
    ) -> None:
        """
        Generate the report and display it.
        """
        _ = only_changes, column_width
        with open(self.__output_path, "w", encoding="utf-8") as outfile:
            outfile.write(f"The file to report on was: {report_file}")

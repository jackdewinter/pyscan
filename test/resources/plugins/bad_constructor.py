import argparse
import os
from typing import Optional, Tuple

from project_summarizer.plugin_manager.project_summarizer_plugin import (
    ProjectSummarizerPlugin,
)
from project_summarizer.summarize_context import SummarizeContext


class BadConstructor(ProjectSummarizerPlugin):
    """
    Class to implement a sample plugin that has a bad constructor, but everything else is okay.
    """

    __COMMAND_LINE_ARGUMENT = "--ctor"
    __COMMAND_LINE_OPTION = "ctor_file"

    def __init__(self, unused: str) -> None:
        super().__init__()
        _ = unused
        self.__output_path: str = ""
        self.__context: Optional[SummarizeContext] = None

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
            BadConstructor.__COMMAND_LINE_ARGUMENT,
            dest=BadConstructor.__COMMAND_LINE_OPTION,
            metavar="path",
            action="store",
            default="",
            help="Source file name for cobertura test coverage reporting.",
        )
        return (
            BadConstructor.__COMMAND_LINE_ARGUMENT,
            BadConstructor.__COMMAND_LINE_OPTION,
        )

    def generate_report(
        self, only_changes: bool, column_width: int, report_file: str
    ) -> None:
        """
        Generate the report and display it.
        """
        pass

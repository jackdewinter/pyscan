"""
Module for the base class for all project_summarizer plugins.
"""

import argparse
import json
import os
import sys
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple

import defusedxml.ElementTree as ET  # type: ignore
from defusedxml.ElementTree import ParseError

from project_summarizer.plugin_manager.plugin_details import PluginDetails
from project_summarizer.summarize_context import SummarizeContext


class ProjectSummarizerPlugin(ABC):
    """
    Base class for all project_summarizer plugins.
    """

    DEFAULT_SUMMARY_PUBLISH_PATH = "publish"
    DEFAULT_REPORT_PUBLISH_PATH = "report"
    DEFAULT_FILE_ENCODING = "utf-8"

    VERSION_BASIC = 1

    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_details(self) -> PluginDetails:
        """
        Get the details for the plugin.
        """

    @abstractmethod
    def set_context(self, context: SummarizeContext) -> None:
        """
        Set the context for the plugins.

        Called from `__main` to set any context in plugins, instead of doing it later.
        """

    @abstractmethod
    def get_output_path(self) -> str:
        """
        Get the output path for the reporting file.

        Used as the destination for the report. Also called from `__publish_summaries`
        to denote the files that need to be published.
        """

    @abstractmethod
    def add_command_line_arguments(
        self, parser: argparse.ArgumentParser
    ) -> Tuple[str, str]:
        """
        Add a command line argument to denote the file to scan.

        Called from function `__parse_arguments` when building the command line.
        """

    @abstractmethod
    def generate_report(
        self, only_changes: bool, column_width: int, report_file: str
    ) -> Optional[Tuple[List[str], List[str], List[List[str]]]]:
        """
        Generate the report and display it.

        Called from function `__create_sumamries` to create the summary file and
        display any results on the console.
        """

    @classmethod
    def load_xml_docment(
        cls,
        xml_file_to_load: str,
        xml_root_element_name: str,
        file_type_name: str,
        format_type_name: str,
    ) -> Any:
        """
        Load a given XML document, check for various formalities along the way.
        """

        if not os.path.exists(xml_file_to_load):
            print(f"Project {file_type_name} file '{xml_file_to_load}' does not exist.")
            sys.exit(1)
        if not os.path.isfile(xml_file_to_load):
            print(f"Project {file_type_name} file '{xml_file_to_load}' is not a file.")
            sys.exit(1)

        try:
            xml_document = ET.parse(xml_file_to_load).getroot()
        except ParseError:
            print(
                f"Project {file_type_name} file '{xml_file_to_load}' is not a valid {file_type_name} file."
            )
            sys.exit(1)

        if xml_document.tag != xml_root_element_name:
            print(
                f"Project {file_type_name} file '{xml_file_to_load}' is not a proper "
                + f"{format_type_name}-format {file_type_name} file."
            )
            sys.exit(1)
        return xml_document

    @classmethod
    def save_summary_file(
        cls,
        json_file_to_write: str,
        object_to_write: Any,
        file_type_name: str,
    ) -> None:
        """
        Save the specified summary file.
        """

        # summary_output_path = os.path.dirname(json_file_to_write)
        # if not os.path.exists(summary_output_path):
        #     print(f"Summary output path '{summary_output_path}' does not exist.")
        #     sys.exit(1)

        full_test_summary_output_path = os.path.abspath(json_file_to_write)
        try:
            with open(
                full_test_summary_output_path,
                "w",
                encoding=ProjectSummarizerPlugin.DEFAULT_FILE_ENCODING,
            ) as outfile:
                if not isinstance(object_to_write, dict):
                    object_to_write = object_to_write.to_dict()
                json.dump(object_to_write, outfile, indent=4)
                outfile.write("\n\n")
        except IOError as ex:
            print(
                f"Project {file_type_name} summary file '{full_test_summary_output_path}"
                + f"' was not written ({ex})."
            )
            sys.exit(1)

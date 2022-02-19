"""
Module for the base class for all project_summarizer plugins.
"""

import json
import os
import sys
from abc import ABC, abstractmethod

import defusedxml.ElementTree as ET
from defusedxml.ElementTree import ParseError


class ProjectSummarizerPlugin(ABC):
    """
    Base class for all project_summarizer plugins.
    """

    DEFAULT_SUMMARY_PUBLISH_PATH = "publish"
    DEFAULT_REPORT_PUBLISH_PATH = "report"
    DEFAULT_FILE_ENCODING = "utf-8"

    def __init__(self):
        pass

    @abstractmethod
    def set_context(self, context):
        """
        Set the context for the plugins.

        Called from `__main` to set any context in plugins, instead of doing it later.
        """

    @abstractmethod
    def get_output_path(self):
        """
        Get the output path for the reporting file.

        Used as the destination for the report. Also called from `__publish_summaries`
        to denote the files that need to be published.
        """

    @abstractmethod
    def add_command_line_arguments(self, parser):
        """
        Add a command line argument to denote the file to scan.

        Called from function `__parse_arguments` when building the command line.
        """

    @abstractmethod
    def generate_report(self, only_changes, column_width, report_file):
        """
        Generate the report and display it.

        Called from function `__create_sumamries` to create the summary file and
        display any results on the console.
        """

    @classmethod
    def load_xml_docment(
        cls, xml_file_to_load, xml_root_element_name, file_type_name, format_type_name
    ):
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
    def save_summary_file(cls, json_file_to_write, object_to_write, file_type_name):
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
                json.dump(object_to_write.to_dict(), outfile, indent=4)
                outfile.write("\n\n")
        except IOError as ex:
            print(
                f"Project {file_type_name} summary file '{full_test_summary_output_path}"
                + f"' was not written ({ex})."
            )
            sys.exit(1)

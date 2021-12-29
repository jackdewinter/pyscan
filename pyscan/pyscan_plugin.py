"""
Module for the base class for all pyscan plugins.
"""

import json
import os
import sys
from abc import ABC, abstractmethod

import defusedxml.ElementTree as ET
from defusedxml.ElementTree import ParseError


class PyScanPlugin(ABC):
    """
    Base class for all pyscan plugins.
    """

    SUMMARY_PUBLISH_PATH = "publish"
    REPORT_PUBLISH_PATH = "report"

    def __init__(self):
        pass

    @abstractmethod
    def get_output_path(self):
        """
        Get the output path for the reporting file.
        """

    @abstractmethod
    def add_command_line_arguments(self, parser):
        """
        Add a command line argument to denote the file to scan.
        """

    @abstractmethod
    def generate_report(self, only_changes, report_file):
        """
        Generate the report and display it.
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

        summary_output_path = os.path.dirname(json_file_to_write)
        if not os.path.exists(summary_output_path):
            print(f"Summary output path '{summary_output_path}' does not exist.")
            sys.exit(1)

        full_test_summary_output_path = os.path.abspath(json_file_to_write)
        try:
            with open(full_test_summary_output_path, "w", encoding="utf-8") as outfile:
                json.dump(object_to_write.to_dict(), outfile, indent=4)
                outfile.write("\n\n")
        except IOError as ex:
            print(
                f"Project {file_type_name} summary file '{full_test_summary_output_path}"
                + f"' was not written ({ex})."
            )
            sys.exit(1)

    @staticmethod
    def compute_published_path_to_file(file_to_publish):
        """
        Compute the path for the given file, assuming it will be placed in the publish directory.
        """

        return os.path.join(
            PyScanPlugin.SUMMARY_PUBLISH_PATH, os.path.basename(file_to_publish)
        )

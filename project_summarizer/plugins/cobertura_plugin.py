"""
Module to provide reporting for coverage files in the Cobertura format.
"""

import argparse
import json
import os
import sys
from typing import Any, List, Optional, Tuple

from project_summarizer.plugin_manager.plugin_details import PluginDetails
from project_summarizer.plugin_manager.project_summarizer_plugin import (
    ProjectSummarizerPlugin,
)
from project_summarizer.plugins.coverage_model import (
    CoverageMeasurement,
    CoverageTotals,
)
from project_summarizer.summarize_context import SummarizeContext


class CoberturaPlugin(ProjectSummarizerPlugin):
    """
    Class to provide reporting for coverage files in the Cobertura format.
    """

    __COMMAND_LINE_ARGUMENT = "--cobertura"
    __COMMAND_LINE_OPTION = "cobertura_coverage_file"

    __PLUGIN_ID = "COBERTURA"
    __PLUGIN_NAME = "Cobertura Coverage Results"
    __PLUGIN_VERSION = "0.5.0"

    __COVERAGE_PY_SIGNATURE = (
        "<!-- Generated by coverage.py: https://coverage.readthedocs.io -->"
    )

    def __init__(self) -> None:
        super().__init__()
        self.__output_path: str = ""
        self.__context: Optional[SummarizeContext] = None

    def get_details(self) -> PluginDetails:
        """
        Get the details for the plugin.
        """
        return PluginDetails(
            CoberturaPlugin.__PLUGIN_ID,
            CoberturaPlugin.__PLUGIN_NAME,
            CoberturaPlugin.__PLUGIN_VERSION,
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

    @classmethod
    def add_command_line_arguments(
        cls, parser: argparse.ArgumentParser
    ) -> Tuple[str, str]:
        """
        Add a command line argument to denote the file to scan.
        """

        parser.add_argument(
            CoberturaPlugin.__COMMAND_LINE_ARGUMENT,
            dest=CoberturaPlugin.__COMMAND_LINE_OPTION,
            metavar="path",
            action="store",
            default="",
            help="Source file name for cobertura test coverage reporting.",
        )
        return (
            CoberturaPlugin.__COMMAND_LINE_ARGUMENT,
            CoberturaPlugin.__COMMAND_LINE_OPTION,
        )

    @classmethod
    def __calculate_coverage_provider(cls, report_file: str) -> str:

        line_count = 0
        combined_lines = None
        with open(
            report_file, "rt", encoding=ProjectSummarizerPlugin.DEFAULT_FILE_ENCODING
        ) as infile:
            next_line = infile.readline()
            while next_line and next_line.strip() != "<sources>" and line_count < 10:
                combined_lines = (
                    f"{combined_lines}\n{next_line[:-1]}"
                    if combined_lines is not None
                    else next_line[:-1]
                )
                next_line = infile.readline()
                line_count += 1

        return (
            "Coverage.py"
            if combined_lines
            and CoberturaPlugin.__COVERAGE_PY_SIGNATURE in combined_lines
            else "Unknown"
        )

    def generate_report(
        self, only_changes: bool, column_width: int, report_file: str
    ) -> Optional[Tuple[List[str], List[str], List[List[str]]]]:
        """
        Generate the report and display it.
        """

        cobertura_document = self.load_xml_docment(
            report_file, "coverage", "test coverage", "Cobertura"
        )
        coverage_provider_name = self.__calculate_coverage_provider(report_file)

        new_stats = self.__compose_summary_from_cobertura_document(
            cobertura_document, coverage_provider_name
        )
        self.save_summary_file(self.__output_path, new_stats, "test coverage")

        if not column_width:
            return None

        assert self.__context is not None
        published_coverage_summary_path = self.__context.compute_published_path_to_file(
            self.__output_path
        )
        loaded_stats = self.__load_coverage_results_summary_file(
            published_coverage_summary_path
        )
        return self.__report_coverage_files(new_stats, loaded_stats, only_changes)

    def __compose_summary_from_cobertura_document(
        self, cobertura_document: Any, coverage_provider_name: str
    ) -> CoverageTotals:
        """
        Compose a CoverageTotals instance from the Cobetura based document.
        """

        project_name = cobertura_document.find("./sources/source").text
        project_name = os.path.basename(project_name)
        coverage_totals = CoverageTotals(
            project_name=project_name, report_source=coverage_provider_name
        )

        measured_lines, covered_lines, measured_branches, covered_branches = 0, 0, 0, 0
        for next_package in cobertura_document.findall("./packages/package"):
            for next_class in next_package.findall("./classes/class"):
                for next_line in next_class.findall("./lines/line"):
                    (
                        covered_line_delta,
                        line_branch_coverage,
                        line_branch_measured,
                    ) = self.__process_line_node(next_line)
                    measured_lines += 1
                    covered_lines += covered_line_delta
                    covered_branches += line_branch_coverage
                    measured_branches += line_branch_measured

        coverage_totals.line_level = CoverageMeasurement(
            total_covered=covered_lines, total_measured=measured_lines
        )
        coverage_totals.branch_level = CoverageMeasurement(
            total_covered=covered_branches, total_measured=measured_branches
        )
        return coverage_totals

    @classmethod
    def __process_line_node(cls, next_line: Any) -> Tuple[int, int, int]:
        """
        Determine the deltas for a line node.
        """

        line_branch_coverage = 0
        line_branch_measured = 0

        line_hits = next_line.attrib["hits"]
        covered_line_delta: int = 1 if line_hits != "0" else 0
        if "condition-coverage" in next_line.attrib:
            line_coverage = next_line.attrib["condition-coverage"]
            start_fraction = line_coverage.index("(")
            end_fraction = line_coverage.index(")", start_fraction)
            coverage_fraction = line_coverage[start_fraction + 1 : end_fraction]
            split_coverage_fraction = coverage_fraction.split("/")
            line_branch_coverage = int(split_coverage_fraction[0])
            line_branch_measured = int(split_coverage_fraction[1])
        return covered_line_delta, line_branch_coverage, line_branch_measured

    @classmethod
    def __load_coverage_results_summary_file(
        cls, test_results_to_load: str
    ) -> Optional[CoverageTotals]:
        """
        Attempt to load a previously published test summary.
        """

        test_totals = None
        if os.path.exists(test_results_to_load) and os.path.isfile(
            test_results_to_load
        ):
            try:
                with open(
                    os.path.abspath(test_results_to_load),
                    "r",
                    encoding=ProjectSummarizerPlugin.DEFAULT_FILE_ENCODING,
                ) as infile:
                    results_dictionary = json.load(infile)
            except json.decoder.JSONDecodeError as ex:
                print(
                    f"Previous coverage summary file '{test_results_to_load}' is not a valid JSON file ({ex})."
                )
                sys.exit(1)
            except IOError as ex:
                print(
                    f"Previous coverage summary file '{test_results_to_load}' was not loaded ({ex})."
                )
                sys.exit(1)
            test_totals = CoverageTotals.from_dict(results_dictionary)
        return test_totals

    def __report_coverage_files(
        self,
        new_stats: CoverageTotals,
        loaded_stats: Optional[CoverageTotals],
        only_report_changes: bool,
    ) -> Optional[Tuple[List[str], List[str], List[List[str]]]]:
        """
        Create a report on coverage.
        """

        if not loaded_stats:
            loaded_stats = CoverageTotals()

        report_rows = self.__calculate_coverage_rows(new_stats, loaded_stats)
        test_report_rows = self.__format_coverage_rows(report_rows, only_report_changes)

        print("\nTest Coverage Summary\n---------------------\n")
        if not test_report_rows:
            print("Test coverage has not changed since last published test coverage.")
            print()
            return None
        justify_columns = ["l", "r", "r", "r"]
        column_headers = ["Type", "Covered", "Measured", "Percentage"]
        return (column_headers, justify_columns, test_report_rows)

    def __calculate_coverage_rows(
        self, new_stats: CoverageTotals, loaded_stats: CoverageTotals
    ) -> List[List[str]]:
        """
        Calculate the coverage rows from the stats objects.
        """

        report_rows = [
            self.__create_coverage_row_contents(
                "Instructions",
                new_stats.instruction_level,
                loaded_stats.instruction_level,
            )
        ]

        report_rows.append(
            self.__create_coverage_row_contents(
                "Lines", new_stats.line_level, loaded_stats.line_level
            )
        )
        report_rows.append(
            self.__create_coverage_row_contents(
                "Branches", new_stats.branch_level, loaded_stats.branch_level
            )
        )
        report_rows.append(
            self.__create_coverage_row_contents(
                "Complexity", new_stats.complexity_level, loaded_stats.complexity_level
            )
        )
        report_rows.append(
            self.__create_coverage_row_contents(
                "Methods", new_stats.method_level, loaded_stats.method_level
            )
        )
        report_rows.append(
            self.__create_coverage_row_contents(
                "Classes", new_stats.class_level, loaded_stats.class_level
            )
        )
        return report_rows

    def __format_coverage_rows(
        self, report_rows: List[List[str]], only_report_changes: bool
    ) -> List[List[str]]:
        """
        Given the coverage data rows, create formatted versions of those rows.
        """

        covered_max_widths = self.__calculate_coverage_column_maximum_widths(
            report_rows, 1
        )
        measured_max_widths = self.__calculate_coverage_column_maximum_widths(
            report_rows, 3
        )
        percentage_max_widths = self.__calculate_coverage_column_maximum_widths(
            report_rows, 5
        )

        test_report_rows: List[List[str]] = []
        for next_row in report_rows:
            formatted_report_row = [next_row[0]]

            formatted_row, row_has_changes = self.__compute_formatted_coverage_column(
                next_row, 1, covered_max_widths
            )
            formatted_report_row.append(formatted_row)

            (
                formatted_row,
                this_row_has_changes,
            ) = self.__compute_formatted_coverage_column(
                next_row, 3, measured_max_widths
            )
            formatted_report_row.append(formatted_row)
            row_has_changes = row_has_changes or this_row_has_changes

            (
                formatted_row,
                this_row_has_changes,
            ) = self.__compute_formatted_coverage_column(
                next_row, 5, percentage_max_widths
            )
            formatted_report_row.append(formatted_row)
            row_has_changes = row_has_changes or this_row_has_changes

            if not only_report_changes or row_has_changes:
                test_report_rows.append(formatted_report_row)

        return test_report_rows

    @classmethod
    def __compute_formatted_coverage_column(
        cls,
        next_row: List[str],
        primary_column_index: int,
        column_maximums: Tuple[int, int],
    ) -> Tuple[str, bool]:
        """
        Compute a properly formatted column value.
        """

        has_changes = False
        if next_row[primary_column_index] == "-":
            column_value = "".rjust(column_maximums[0], "-")
        else:
            column_value = next_row[primary_column_index].rjust(column_maximums[0], " ")
        if column_maximums[1] != 0:
            if next_row[primary_column_index + 1] == "-":
                column_value = f"{column_value} " + " ".rjust(
                    column_maximums[1] + 2, " "
                )
            else:
                partial_value = next_row[primary_column_index + 1]
                has_changes = partial_value.startswith("+") or partial_value.startswith(
                    "-"
                )
                partial_value = partial_value.rjust(column_maximums[1], " ")
                column_value = f"{column_value} ({partial_value})"
        return column_value, has_changes

    @classmethod
    def __calculate_coverage_column_maximum_widths(
        cls, report_rows: List[List[str]], primary_column_index: int
    ) -> Tuple[int, int]:
        """
        Calculate the maximum widths over all of the columns in all the report rows.
        """
        primary_max = 0
        secondary_max = 0
        for next_row in report_rows:
            column_value = next_row[primary_column_index]
            primary_max = max(len(column_value), primary_max)
            column_value = next_row[primary_column_index + 1]
            if column_value not in ("-", "0", "0.00"):
                secondary_max = max(len(column_value), secondary_max)
        return primary_max, secondary_max

    @classmethod
    def __create_coverage_row_contents(
        cls,
        coverage_name: str,
        current_stats: Optional[CoverageMeasurement],
        loaded_stats: Optional[CoverageMeasurement],
    ) -> List[str]:
        """
        Create a row of contents for the coverage item.
        """
        new_row: List[str] = [coverage_name]
        if current_stats:
            covered_value = current_stats.total_covered
            measured_value = current_stats.total_measured
            percentage_value = 100.0 * (float(covered_value) / float(measured_value))
            if loaded_stats:
                loaded_percentage_value = 100.0 * (
                    float(loaded_stats.total_covered)
                    / float(loaded_stats.total_measured)
                )
                delta_covered_value = covered_value - loaded_stats.total_covered
                delta_measured_value = measured_value - loaded_stats.total_measured
                delta_percentage_value = percentage_value - loaded_percentage_value

                cls.__format_coverage_value(
                    new_row, str(covered_value), str(delta_covered_value)
                )
                cls.__format_coverage_value(
                    new_row, str(measured_value), str(delta_measured_value)
                )
                cls.__format_coverage_value(
                    new_row,
                    f"{percentage_value:.2f}",
                    f"{delta_percentage_value:.2f}",
                )
            else:
                cls.__format_coverage_value(
                    new_row, str(covered_value), str(covered_value)
                )
                cls.__format_coverage_value(
                    new_row, str(measured_value), str(measured_value)
                )
                cls.__format_coverage_value(
                    new_row,
                    f"{percentage_value:.2f}",
                    f"{percentage_value:.2f}",
                )
        else:
            new_row.extend("-" for _ in range(6))
        return new_row

    # pylint: disable=unused-private-member
    @classmethod
    def __format_coverage_value(
        cls, new_row: List[str], value: str, delta: str
    ) -> None:
        """
        Helper method to consistently format the coverage value/delta.
        """
        new_row.append(value)
        delta_value = delta
        if (
            delta_value != "0"
            and delta_value != "0.00"
            and not delta_value.startswith("-")
        ):
            delta_value = f"+{delta_value}"
        new_row.append(delta_value)

    # pylint: enable=unused-private-member

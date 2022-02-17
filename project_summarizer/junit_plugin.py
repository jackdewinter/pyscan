"""
Module to provide reporting for test files in the JUnit format.
"""

import difflib
import json
import os
import sys

from columnar import columnar

from project_summarizer.project_summarizer_plugin import ProjectSummarizerPlugin
from project_summarizer.test_results_model import TestMeasurement, TestTotals


class JUnitPlugin(ProjectSummarizerPlugin):
    """
    Class to provide reporting for test files in the JUnit format.
    """

    __COMMAND_LINE_ARGUMENT = "--junit"
    __COMMAND_LINE_OPTION = "test_report_file"

    def __init__(self):
        super().__init__()
        self.__output_path = os.path.join(self.REPORT_PUBLISH_PATH, "test-results.json")

    def get_output_path(self):
        """
        Get the output path for the reporting file.
        """
        return self.__output_path

    @classmethod
    def add_command_line_arguments(cls, parser):
        """
        Add a command line argument to denote the file to scan.
        """

        parser.add_argument(
            JUnitPlugin.__COMMAND_LINE_ARGUMENT,
            dest=JUnitPlugin.__COMMAND_LINE_OPTION,
            metavar="path",
            action="store",
            default="",
            help="source file name for junit test result reporting",
        )
        return (
            JUnitPlugin.__COMMAND_LINE_ARGUMENT,
            JUnitPlugin.__COMMAND_LINE_OPTION,
        )

    def generate_report(self, only_changes, column_width, report_file):
        """
        Generate the report and display it.
        """
        junit_document = self.load_xml_docment(
            report_file, "testsuites", "test report", "Junit"
        )

        new_stats, new_totals = self.__compose_summary_from_junit_document(
            junit_document
        )
        self.save_summary_file(self.__output_path, new_stats, "test report")

        if column_width:
            published_test_summary_path = self.compute_published_path_to_file(
                self.__output_path
            )
            loaded_stats, loaded_totals = self.load_test_results_summary_file(
                published_test_summary_path
            )
            self.__report_test_files(
                new_stats,
                new_totals,
                loaded_stats,
                loaded_totals,
                only_changes,
                column_width,
            )

    def __compose_summary_from_junit_document(self, junit_document):
        """
        Read the values from the junit document and construct a TestTotals instance
        summary from the data.
        """

        test_totals = TestTotals(project_name="?", report_source="pytest")
        for next_test_suite in junit_document.findall("testsuite"):
            for next_test_case in next_test_suite.findall("./testcase"):
                class_name = next_test_case.attrib["classname"]
                did_skip = False
                did_fail = False

                if class_name in test_totals.measurements:
                    measurement_to_add_to = test_totals.measurements[class_name]
                else:
                    measurement_to_add_to = TestMeasurement(class_name)
                    test_totals.measurements[class_name] = measurement_to_add_to
                for next_child_node in next_test_case:
                    if next_child_node.tag == "failure":
                        did_fail = True
                    elif next_child_node.tag == "skipped":
                        did_skip = True
                if did_fail:
                    measurement_to_add_to.failed_tests = (
                        measurement_to_add_to.failed_tests + 1
                    )
                elif did_skip:
                    measurement_to_add_to.skipped_tests = (
                        measurement_to_add_to.skipped_tests + 1
                    )
                measurement_to_add_to.total_tests = (
                    measurement_to_add_to.total_tests + 1
                )

        grand_totals = self.__build_totals(test_totals)
        return test_totals, grand_totals

    @classmethod
    def __build_totals(cls, test_totals):
        """
        Calculate the grand totals based on the test totals object presented.
        """

        grand_totals = TestMeasurement("totals")
        for next_key in sorted(test_totals.measurements):
            next_value = test_totals.measurements[next_key]
            grand_totals.total_tests = grand_totals.total_tests + next_value.total_tests
            grand_totals.skipped_tests = (
                grand_totals.skipped_tests + next_value.skipped_tests
            )
            grand_totals.failed_tests = (
                grand_totals.failed_tests + next_value.failed_tests
            )
        return grand_totals

    def load_test_results_summary_file(self, test_results_to_load):
        """
        Attempt to load a previously published test summary.
        """

        test_totals, grand_totals = None, None
        if os.path.exists(test_results_to_load) and os.path.isfile(
            test_results_to_load
        ):
            try:
                with open(
                    os.path.abspath(test_results_to_load), "r", encoding="utf-8"
                ) as infile:
                    results_dictionary = json.load(infile)
            except json.decoder.JSONDecodeError as ex:
                print(
                    f"Previous results summary file '{test_results_to_load}' is not a valid JSON file ({ex})."
                )
                sys.exit(1)
            except IOError as ex:
                print(
                    f"Previous results summary file '{test_results_to_load}' was not loaded ({ex})."
                )
                sys.exit(1)
            test_totals = TestTotals.from_dict(results_dictionary)
            grand_totals = self.__build_totals(test_totals)
        return test_totals, grand_totals

    # pylint: disable=too-many-arguments, too-many-locals
    def __report_test_files(
        self,
        new_stats,
        new_totals,
        loaded_stats,
        loaded_totals,
        only_report_changes,
        column_width,
    ):
        """
        Generate a report comparing the current stats with the loaded/previous stats.
        """

        if not loaded_stats:
            loaded_stats = TestTotals()
        if not loaded_totals:
            loaded_totals = TestMeasurement("default")

        new_stats_keys = sorted(list(new_stats.measurements.keys()))
        loaded_stats_keys = sorted(list(loaded_stats.measurements.keys()))

        test_report_rows = []
        for next_output in difflib.ndiff(new_stats_keys, loaded_stats_keys):
            next_output_prefix = next_output[:2]
            next_output_name = next_output[2:]

            row_to_add = None
            if next_output_prefix == "  ":
                new_measurement = new_stats.measurements[next_output_name]
                loaded_measurement = loaded_stats.measurements[next_output_name]
                row_to_add = self.__generate_full_match(
                    next_output_name, new_measurement, loaded_measurement
                )
            elif next_output_prefix == "+ ":
                loaded_measurement = loaded_stats.measurements[next_output_name]
                row_to_add = self.__generate_older_match(
                    next_output_name, loaded_measurement
                )
            elif next_output_prefix == "- ":
                new_measurement = new_stats.measurements[next_output_name]
                row_to_add = self.__generate_newer_match(
                    next_output_name, new_measurement
                )

            if row_to_add:
                self.__add_row_to_report(
                    row_to_add, test_report_rows, only_report_changes
                )

        self.print_test_summary(
            test_report_rows, new_totals, loaded_totals, column_width
        )

    # pylint: enable=too-many-arguments, too-many-locals

    @classmethod
    def __generate_match_column(cls, value_to_display, delta_to_display):
        """
        Given a value column and a delta column, combine these two values into one value to display.
        """

        if delta_to_display > 0:
            return f"{value_to_display} +{delta_to_display}"
        return f"{value_to_display} {delta_to_display}"

    # pylint: disable=too-many-arguments
    def __generate_match(
        self,
        class_name,
        total_value,
        total_delta,
        failed_value,
        failed_delta,
        skipped_value,
        skipped_delta,
    ):
        """
        Helper method to generate the columns based on previous inputs.
        """

        return [
            class_name,
            self.__generate_match_column(total_value, total_delta),
            self.__generate_match_column(failed_value, failed_delta),
            self.__generate_match_column(skipped_value, skipped_delta),
        ]

    # pylint: enable=too-many-arguments

    def __generate_full_match(self, class_name, newer_measure, older_measure):
        """
        Helper method to generate a match with both a newer measurement and an older measurement.
        """

        return self.__generate_match(
            class_name,
            newer_measure.total_tests,
            newer_measure.total_tests - older_measure.total_tests,
            newer_measure.failed_tests,
            newer_measure.failed_tests - older_measure.failed_tests,
            newer_measure.skipped_tests,
            newer_measure.skipped_tests - older_measure.skipped_tests,
        )

    def __generate_older_match(self, class_name, older_measure):
        """
        Helper method to generate a match with only an older measurement.
        """

        return self.__generate_match(
            class_name,
            -1,
            -older_measure.total_tests,
            -1,
            -older_measure.failed_tests,
            -1,
            -older_measure.skipped_tests,
        )

    def __generate_newer_match(self, class_name, newer_measure):
        """
        Helper method to generate a match with only a newer measurement.
        """

        return self.__generate_match(
            class_name,
            newer_measure.total_tests,
            newer_measure.total_tests,
            newer_measure.failed_tests,
            newer_measure.failed_tests,
            newer_measure.skipped_tests,
            newer_measure.skipped_tests,
        )

    @classmethod
    def __format_test_totals_column(cls, source_array, column_index):
        """
        For a given column in "1 0" or "-1 2" format, ensure that the right
        replacements are done to show the column properly and properly formatted.
        """

        max_width_1 = 0
        max_width_2 = 0
        for next_row in source_array:
            split_row = next_row[column_index].split(" ")
            if split_row[0] != "-1":
                max_width_1 = max(max_width_1, len(split_row[0]))
            if split_row[1] != "0":
                max_width_2 = max(max_width_2, len(split_row[1]) + 2)

        for next_row in source_array:
            split_row = next_row[column_index].split(" ")
            if split_row[0] != "-1":
                new_value = split_row[0].rjust(max_width_1, " ")
            else:
                new_value = "".rjust(max_width_1, "-")
            next_row[column_index] = new_value
            if max_width_2 != 0:
                if split_row[1] != "0":
                    new_value = f"({split_row[1]})"
                    new_value = new_value.rjust(max_width_2, " ")
                else:
                    new_value = "".rjust(max_width_2, " ")
                next_row[column_index] = f"{next_row[column_index]} {new_value}"

    def print_test_summary(
        self, test_report_rows, new_totals, loaded_totals, column_width
    ):
        """
        Print the actual test summaries.
        """

        print("\nTest Results Summary\n--------------------\n")
        if not test_report_rows:
            print("Test results have not changed since last published test results.")
        else:
            test_report_rows.append(["---", "-1 0", "-1 0", "-1 0"])
            test_report_rows.append(
                self.__generate_full_match("TOTALS", new_totals, loaded_totals)
            )

            self.__format_test_totals_column(test_report_rows, 1)
            self.__format_test_totals_column(test_report_rows, 2)
            self.__format_test_totals_column(test_report_rows, 3)

            hdrs = ["Class Name", "Total Tests", "Failed Tests", "Skipped Tests"]

            table = columnar(
                test_report_rows,
                headers=hdrs,
                no_borders=True,
                justify=["l", "r", "r", "r"],
                terminal_width=column_width if column_width != -1 else None,
            )
            split_rows = table.split("\n")
            new_rows = [next_row.rstrip() for next_row in split_rows]
            print("\n".join(new_rows))

    @classmethod
    def __add_row_to_report(cls, row_to_add, test_report_rows, only_report_changes):
        """
        Determine if adequate requirements exist to add the specified row to the report.
        """

        did_change = any(
            "+" in row_to_add[column_number] or "-" in row_to_add[column_number]
            for column_number in range(1, len(row_to_add))
        )

        if not only_report_changes or did_change:
            test_report_rows.append(row_to_add)

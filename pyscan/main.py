"""
Module to provide for a simple summarization of relevant output files from a build.
"""
import argparse
import difflib
import json
import os
import sys
from shutil import copyfile

import defusedxml.ElementTree as ET
from columnar import columnar
from defusedxml.ElementTree import ParseError

from pyscan.model import (
    CoverageMeasurement,
    CoverageTotals,
    TestMeasurement,
    TestTotals,
)


class PyScan:
    """
    Class to provide for a simple summarization of relevant output files from a build.
    """

    def __init__(self):
        self.version_number = "0.1.0"
        self.test_summary_output_path = os.path.join("report", "test-results.json")
        self.coverage_summary_output_path = os.path.join("report", "coverage.json")
        self.test_summary_publish_path = "publish"
        self.debug = False

    def __parse_arguments(self):
        """
        Handle any arguments for the program.
        """

        parser = argparse.ArgumentParser(description="Summarize Python files.")

        parser.add_argument(
            "--version", action="version", version="%(prog)s " + self.version_number
        )

        parser.add_argument(
            "--junit",
            dest="test_report_file",
            metavar="path",
            action="store",
            default="",
            help="source file for any reporting on test success",
        )
        parser.add_argument(
            "--cobertura",
            dest="test_coverage_file",
            metavar="path",
            action="store",
            default="",
            help="source file for any reporting on test coverage",
        )
        parser.add_argument(
            "--only-changes",
            dest="only_changes",
            action="store_true",
            default=False,
            help="only_changes",
        )
        parser.add_argument(
            "--publish",
            dest="publish_summaries",
            action="store_true",
            default=False,
            help="publish",
        )
        args = parser.parse_args()
        if (
            not args.publish_summaries
            and not args.test_coverage_file
            and not args.test_report_file
        ):
            parser.print_help()
            sys.exit(2)
        return args

    def __publish_file(self, file_to_publish):
        """
        Publish the specified file to the set publish directory.
        """

        if not os.path.exists(self.test_summary_publish_path):
            print(
                f"Publish directory '{self.test_summary_publish_path}' does not exist.  Creating."
            )
            os.makedirs(self.test_summary_publish_path)
        elif not os.path.isdir(self.test_summary_publish_path):
            print(
                f"Publish directory '{self.test_summary_publish_path}' already exists, but as a file."
            )
            sys.exit(1)

        if os.path.exists(file_to_publish):
            try:
                copyfile(
                    file_to_publish,
                    self.compute_published_path_to_file(file_to_publish),
                )
            except IOError as ex:
                print(f"Publishing file '{file_to_publish}' failed ({ex}).")
                sys.exit(1)

    def compute_published_path_to_file(self, file_to_publish):
        """
        Compute the path for the given file, assuming it will be placed in the publish directory.
        """

        return os.path.join(
            self.test_summary_publish_path, os.path.basename(file_to_publish)
        )

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

    @classmethod
    def load_coverage_results_summary_file(cls, test_results_to_load):
        """
        Attempt to load a previously published test summary.
        """

        test_totals = None
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

    def compose_summary_from_junit_document(self, junit_document):
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
    def __process_line_node(cls, next_line):
        """
        Determine the deltas for a line node.
        """

        line_branch_coverage = 0
        line_branch_measured = 0

        line_hits = next_line.attrib["hits"]
        covered_line_delta = 1 if line_hits != "0" else 0
        if "condition-coverage" in next_line.attrib:
            line_coverage = next_line.attrib["condition-coverage"]
            start_fraction = line_coverage.index("(")
            end_fraction = line_coverage.index(")", start_fraction)
            coverage_fraction = line_coverage[start_fraction + 1 : end_fraction]
            split_coverage_fraction = coverage_fraction.split("/")
            line_branch_coverage = int(split_coverage_fraction[0])
            line_branch_measured = int(split_coverage_fraction[1])
        return covered_line_delta, line_branch_coverage, line_branch_measured

    def compose_summary_from_cobertura_document(self, cobertura_document):
        """
        Compose a CoverageTotals instance from the Cobetura based document.
        """

        project_name = cobertura_document.find("./sources/source").text
        project_name = os.path.basename(project_name)
        coverage_totals = CoverageTotals(
            project_name=project_name, report_source="pytest"
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
                    new_value = "(" + split_row[1] + ")"
                    new_value = new_value.rjust(max_width_2, " ")
                else:
                    new_value = "".rjust(max_width_2, " ")
                next_row[column_index] = next_row[column_index] + " " + new_value

    def print_test_summary(self, test_report_rows, new_totals, loaded_totals):
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

    def __calculate_coverage_rows(self, new_stats, loaded_stats):
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

    def __format_coverage_rows(self, report_rows, only_report_changes):
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

        test_report_rows = []
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

    def __report_coverage_files(self, new_stats, loaded_stats, only_report_changes):
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
        else:
            hdrs = ["Type", "Covered", "Measured", "Percentage"]
            table = columnar(
                test_report_rows,
                headers=hdrs,
                no_borders=True,
                justify=["l", "r", "r", "r"],
            )
            split_rows = table.split("\n")
            new_rows = [next_row.rstrip() for next_row in split_rows]
            print("\n".join(new_rows))
        print()

    @classmethod
    def __compute_formatted_coverage_column(
        cls, next_row, primary_column_index, column_maximums
    ):
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
                column_value = (
                    column_value + " " + " ".rjust(column_maximums[1] + 2, " ")
                )
            else:
                partial_value = next_row[primary_column_index + 1]
                has_changes = partial_value.startswith("+") or partial_value.startswith(
                    "-"
                )
                partial_value = partial_value.rjust(column_maximums[1], " ")
                column_value = column_value + " (" + partial_value + ")"
        return column_value, has_changes

    @classmethod
    def __calculate_coverage_column_maximum_widths(
        cls, report_rows, primary_column_index
    ):
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
    def __create_coverage_row_contents(cls, coverage_name, current_stats, loaded_stats):
        """
        Create a row of contents for the coverage item.
        """
        new_row = [coverage_name]
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
            for _ in range(6):
                new_row.append("-")
        return new_row

    # pylint: disable=unused-private-member
    @classmethod
    def __format_coverage_value(cls, new_row, value, delta):
        """
        Helper method to consistently format the coverage value/delta.
        """
        new_row.append(value)
        delta_value = str(delta)
        if (
            delta_value != "0"
            and delta_value != "0.00"
            and not delta_value.startswith("-")
        ):
            delta_value = "+" + delta_value
        new_row.append(delta_value)

    # pylint: enable=unused-private-member

    # pylint: disable=too-many-arguments
    def __report_test_files(
        self, new_stats, new_totals, loaded_stats, loaded_totals, only_report_changes
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

        self.print_test_summary(test_report_rows, new_totals, loaded_totals)

    # pylint: enable=too-many-arguments

    def publish_summaries(self):
        """
        Respond to a request to publish any existing summaries.
        """

        if os.path.exists(self.test_summary_output_path) and not os.path.isfile(
            self.test_summary_output_path
        ):
            print(
                f"Test results summary path '{self.test_summary_output_path}' is not a file."
            )
            sys.exit(1)
        if os.path.exists(self.coverage_summary_output_path) and not os.path.isfile(
            self.coverage_summary_output_path
        ):
            print(
                f"Test coverage summary path '{self.coverage_summary_output_path}' is not a file."
            )
            sys.exit(1)

        self.__publish_file(self.test_summary_output_path)
        self.__publish_file(self.coverage_summary_output_path)

    @classmethod
    def __load_xml_docment(
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
    def __save_summary_file(cls, json_file_to_write, object_to_write, file_type_name):
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
                json.dump(object_to_write.to_dict(), outfile)
        except IOError as ex:
            print(
                f"Project {file_type_name} summary file '{full_test_summary_output_path}"
                + f"' was not written ({ex})."
            )
            sys.exit(1)

    def generate_test_report(self, args):
        """
        Respond to a request to generate a test report.
        """

        junit_document = self.__load_xml_docment(
            args.test_report_file, "testsuites", "test report", "Junit"
        )

        new_stats, new_totals = self.compose_summary_from_junit_document(junit_document)
        self.__save_summary_file(
            self.test_summary_output_path, new_stats, "test report"
        )

        published_test_summary_path = self.compute_published_path_to_file(
            self.test_summary_output_path
        )
        loaded_stats, loaded_totals = self.load_test_results_summary_file(
            published_test_summary_path
        )

        self.__report_test_files(
            new_stats, new_totals, loaded_stats, loaded_totals, args.only_changes
        )

    def generate_coverage_report(self, args):
        """
        Generate the coverage report and display it.
        """

        cobertura_document = self.__load_xml_docment(
            args.test_coverage_file, "coverage", "test coverage", "Cobertura"
        )

        new_stats = self.compose_summary_from_cobertura_document(cobertura_document)
        self.__save_summary_file(
            self.coverage_summary_output_path, new_stats, "test coverage"
        )

        published_coverage_summary_path = self.compute_published_path_to_file(
            self.coverage_summary_output_path
        )
        loaded_stats = self.load_coverage_results_summary_file(
            published_coverage_summary_path
        )

        self.__report_coverage_files(new_stats, loaded_stats, args.only_changes)

    def main(self):
        """
        Main entrance point.
        """
        args = self.__parse_arguments()

        if args.publish_summaries:
            self.publish_summaries()
            sys.exit(0)

        if args.test_report_file:
            self.generate_test_report(args)
        if args.test_coverage_file:
            self.generate_coverage_report(args)


if __name__ == "__main__":
    PyScan().main()

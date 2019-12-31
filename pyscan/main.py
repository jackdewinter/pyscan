"""
Module to provide for a simple summarization of relevant output files from a build.
"""
import argparse
import difflib
import json
import os
import sys
from shutil import copyfile
from xml.etree import ElementTree as ET

import tabulate as tabulate_module
from tabulate import tabulate


class TestTotals:
    """
    Class to provide an encapsulation of the test totals.
    """

    def __init__(self, project_name=None, report_source=None):
        self.project_name = project_name
        self.report_source = report_source
        self.measurements = {}

    def to_dict(self):
        """
        Convert the current totals into a vanilla dictionary.
        """

        serialized_dictionary = {}
        serialized_dictionary["projectName"] = self.project_name
        serialized_dictionary["reportSource"] = self.report_source
        measurements_array = []
        for next_measurement in self.measurements:
            serialized_measurement = self.measurements[next_measurement].to_dict()
            measurements_array.append(serialized_measurement)
        serialized_dictionary["measurements"] = measurements_array
        return serialized_dictionary

    @staticmethod
    def from_dict(input_dictionary):
        """
        Read the totals in from the specified dictionary.
        """

        total_project = input_dictionary["projectName"]
        total_report = input_dictionary["reportSource"]
        total_measurements = input_dictionary["measurements"]
        new_total = TestTotals(project_name=total_project, report_source=total_report)
        for next_measurement_name in total_measurements:
            next_measurement = TestMeasurement.from_dict(next_measurement_name)
            new_total.measurements[next_measurement.name] = next_measurement
        return new_total


class TestMeasurement:
    """
    Class to provide an encapsulation of the test measurements.
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        name,
        total_tests=0,
        failed_tests=0,
        skipped_tests=0,
        error_tests=0,
        elapsed_time_ms=0,
    ):
        self.name = name
        self.total_tests = total_tests
        self.failed_tests = failed_tests
        self.error_tests = error_tests
        self.skipped_tests = skipped_tests
        self.elapsed_time_ms = elapsed_time_ms

    # pylint: enable=too-many-arguments

    def to_dict(self):
        """
        Convert the current measurement into a vanilla dictionary.
        """

        serialized_dictionary = {}
        serialized_dictionary["name"] = self.name
        serialized_dictionary["totalTests"] = self.total_tests
        serialized_dictionary["failedTests"] = self.failed_tests
        serialized_dictionary["errorTests"] = self.error_tests
        serialized_dictionary["skippedTests"] = self.skipped_tests
        serialized_dictionary["elapsedTimeInMilliseconds"] = self.elapsed_time_ms
        return serialized_dictionary

    @staticmethod
    def from_dict(input_dictionary):
        """
        Read the measurement in from the specified dictionary.
        """

        measure_name = input_dictionary["name"]
        measure_total = input_dictionary["totalTests"]
        measure_failed = input_dictionary["failedTests"]
        measure_errored = input_dictionary["errorTests"]
        measure_skipped = input_dictionary["skippedTests"]
        measure_elapsed = input_dictionary["elapsedTimeInMilliseconds"]
        new_measurement = TestMeasurement(
            name=measure_name,
            total_tests=measure_total,
            failed_tests=measure_failed,
            error_tests=measure_errored,
            skipped_tests=measure_skipped,
            elapsed_time_ms=measure_elapsed,
        )
        return new_measurement


class PyScan:
    """
    Class to provide for a simple summarization of relevant output files from a build.
    """

    def __init__(self):
        self.version_number = "0.1.0"
        self.test_summary_output_path = "report/test-results.json"
        self.test_summary_publish_path = "publish"

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
        return parser.parse_args()

    def publish_file(self, file_to_publish):
        """
        Publish the specified file to the set publish directory.
        """

        if not os.path.exists(self.test_summary_publish_path):
            print(
                "Publish directory '"
                + self.test_summary_publish_path
                + "' does not exist.  Creating."
            )
            os.makedirs(self.test_summary_publish_path)
        elif not os.path.isdir(self.test_summary_publish_path):
            print(
                "Publish directory '"
                + self.test_summary_publish_path
                + "' already exists, but as a file."
            )
            sys.exit(1)

        # TODO what if fails?
        copyfile(file_to_publish, self.compute_published_path_to_file(file_to_publish))

    def compute_published_path_to_file(self, file_to_publish):
        """
        Compute the path for the given file, assuming it will be placed in the publish directory.
        """

        destination_path = os.path.join(
            self.test_summary_publish_path, os.path.basename(file_to_publish)
        )
        return destination_path

    def load_test_results_summary_file(self, test_results_to_load):
        """
        Attempt to load a previously published test sumary.
        """

        # TODO what if fails?
        with open(test_results_to_load, "r") as infile:
            results_dictionary = json.load(infile)
        test_totals = TestTotals.from_dict(results_dictionary)
        grand_totals = self.build_totals(test_totals)
        return test_totals, grand_totals

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
                    if next_child_node.tag == "skipped":
                        did_skip = True
                    if next_child_node.tag == "failure":
                        did_fail = True
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

        grand_totals = self.build_totals(test_totals)
        return test_totals, grand_totals

    @classmethod
    def build_totals(cls, test_totals):
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
    def generate_match_column(cls, value_to_display, delta_to_display):
        """
        Given a value column and a delta column, combine these two values into one value to display.
        """

        if delta_to_display > 0:
            return str(value_to_display) + " +" + str(delta_to_display)
        return str(value_to_display) + " " + str(delta_to_display)

    # pylint: disable=too-many-arguments
    def generate_match(
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
            self.generate_match_column(total_value, total_delta),
            self.generate_match_column(failed_value, failed_delta),
            self.generate_match_column(skipped_value, skipped_delta),
        ]

    # pylint: enable=too-many-arguments

    def generate_full_match(self, class_name, newer_measure, older_measure):
        """
        Helper method to generate a match with both a newer measurement and an older measurement.
        """

        return self.generate_match(
            class_name,
            newer_measure.total_tests,
            newer_measure.total_tests - older_measure.total_tests,
            newer_measure.failed_tests,
            newer_measure.failed_tests - older_measure.failed_tests,
            newer_measure.skipped_tests,
            newer_measure.skipped_tests - older_measure.skipped_tests,
        )

    def generate_older_match(self, class_name, older_measure):
        """
        Helper method to generate a match with only an older measurement.
        """

        return self.generate_match(
            class_name,
            -1,
            -older_measure.total_tests,
            -1,
            -older_measure.failed_tests,
            -1,
            -older_measure.skipped_tests,
        )

    def generate_newer_match(self, class_name, newer_measure):
        """
        Helper method to generate a match with only a newer measurement.
        """

        return self.generate_match(
            class_name,
            newer_measure.total_tests,
            newer_measure.total_tests,
            newer_measure.failed_tests,
            newer_measure.failed_tests,
            newer_measure.skipped_tests,
            newer_measure.skipped_tests,
        )

    @classmethod
    def format_test_totals_column(cls, source_array, column_index):
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
                max_width_2 = max(max_width_1, len(split_row[1]) + 2)

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
                self.generate_full_match("TOTALS", new_totals, loaded_totals)
            )

            self.format_test_totals_column(test_report_rows, 1)
            self.format_test_totals_column(test_report_rows, 2)
            self.format_test_totals_column(test_report_rows, 3)

            hdrs = ["Class Name", "Total Tests", "Failed Tests", "Skipped Tests"]

            tabulate_module.MIN_PADDING = 1
            tabulate_module.PRESERVE_WHITESPACE = True
            print(
                tabulate(
                    test_report_rows,
                    headers=hdrs,
                    tablefmt="simple",
                    colalign=("left", "right", "right", "right"),
                )
            )

    @classmethod
    def add_row_to_report(cls, row_to_add, test_report_rows, only_report_changes):
        """
        Determine if adequate requirements exist to add the specified row to the report.
        """

        did_change = False
        for column_number in range(1, len(row_to_add)):
            if "+" in row_to_add[column_number] or "-" in row_to_add[column_number]:
                did_change = True
        if not only_report_changes or did_change:
            test_report_rows.append(row_to_add)

    # pylint: disable=too-many-arguments
    def report_test_files(
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
            next_output_prefix = next_output[0:2]
            next_output_name = next_output[2:]

            row_to_add = None
            if next_output_prefix == "  ":
                new_measurement = new_stats.measurements[next_output_name]
                loaded_measurement = loaded_stats.measurements[next_output_name]
                row_to_add = self.generate_full_match(
                    next_output_name, new_measurement, loaded_measurement
                )
            elif next_output_prefix == "+ ":
                loaded_measurement = loaded_stats.measurements[next_output_name]
                row_to_add = self.generate_older_match(
                    next_output_name, loaded_measurement
                )
            elif next_output_prefix == "- ":
                new_measurement = new_stats.measurements[next_output_name]
                row_to_add = self.generate_newer_match(
                    next_output_name, new_measurement
                )

            if row_to_add:
                self.add_row_to_report(
                    row_to_add, test_report_rows, only_report_changes
                )

        self.print_test_summary(test_report_rows, new_totals, loaded_totals)

    # pylint: enable=too-many-arguments

    def publish_summaries(self):
        """
        Respond to a request to publish any existing summaries.
        """

        if not os.path.exists(self.test_summary_output_path):
            print(
                "Test results summary file '"
                + self.test_summary_output_path
                + "' does not exist."
            )
            sys.exit(1)
        if not os.path.isfile(self.test_summary_output_path):
            print(
                "Test results summary path '"
                + self.test_summary_output_path
                + "' is not a file."
            )
            sys.exit(1)

        self.publish_file(self.test_summary_output_path)

    def generate_test_report(self, args):
        """
        Respond to a request to generate a test report.
        """

        if not os.path.exists(args.test_report_file):
            print(
                "Project test report file '"
                + args.test_report_file
                + "' does not exist."
            )
            sys.exit(1)
        if not os.path.isfile(args.test_report_file):
            print(
                "Project test report file '"
                + args.test_report_file
                + "' is not a file."
            )
            sys.exit(1)

        # TODO what if fails?
        junit_document = ET.parse(args.test_report_file).getroot()

        # TODO what if fails?
        if junit_document.tag != "testsuites":
            print(
                "Project test report file '"
                + args.test_report_file
                + "' is not a proper Junit-format test report file."
            )
            sys.exit(1)

        new_stats, new_totals = self.compose_summary_from_junit_document(junit_document)
        # TODO what if fails?

        summary_output_path = os.path.dirname(self.test_summary_output_path)
        if not os.path.exists(summary_output_path):
            print("Summary output path '" + summary_output_path + "' does not exist.")
            sys.exit(1)

        with open(self.test_summary_output_path, "w") as outfile:
            json.dump(new_stats.to_dict(), outfile)

        loaded_stats = None
        loaded_totals = None
        published_test_summary_path = self.compute_published_path_to_file(
            self.test_summary_output_path
        )
        if os.path.exists(published_test_summary_path) and os.path.isfile(
            published_test_summary_path
        ):
            loaded_stats, loaded_totals = self.load_test_results_summary_file(
                published_test_summary_path
            )

        self.report_test_files(
            new_stats, new_totals, loaded_stats, loaded_totals, args.only_changes
        )

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


if __name__ == "__main__":
    PyScan().main()

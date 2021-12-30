"""
Module to contain the model objects used to contain test results information.
"""


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

        serialized_dictionary = {
            "projectName": self.project_name,
            "reportSource": self.report_source,
        }

        measurements_array = [
            next_measurement.to_dict()
            for _, next_measurement in self.measurements.items()
        ]

        measurements_array = sorted(measurements_array, key=lambda item: item["name"])

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

        return {
            "name": self.name,
            "totalTests": self.total_tests,
            "failedTests": self.failed_tests,
            "errorTests": self.error_tests,
            "skippedTests": self.skipped_tests,
            "elapsedTimeInMilliseconds": self.elapsed_time_ms,
        }

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
        return TestMeasurement(
            name=measure_name,
            total_tests=measure_total,
            failed_tests=measure_failed,
            error_tests=measure_errored,
            skipped_tests=measure_skipped,
            elapsed_time_ms=measure_elapsed,
        )

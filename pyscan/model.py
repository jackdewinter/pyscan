"""
Module to contain the model objects used to contain various summary information.
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
            'projectName': self.project_name,
            'reportSource': self.report_source,
        }

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

        return {
            'name': self.name,
            'totalTests': self.total_tests,
            'failedTests': self.failed_tests,
            'errorTests': self.error_tests,
            'skippedTests': self.skipped_tests,
            'elapsedTimeInMilliseconds': self.elapsed_time_ms,
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


class CoverageMeasurement:
    """
    Class to contain information about coverage measurements.
    """

    def __init__(
        self, total_covered, total_measured,
    ):
        self.total_covered = total_covered
        self.total_measured = total_measured

    def __eq__(self, other):
        """
        Overrides the default implementation
        """
        if isinstance(other, CoverageMeasurement):
            return (
                self.total_covered == other.total_covered
                and self.total_measured == other.total_measured
            )
        return NotImplemented

    def to_dict(self):
        """
        Convert the current measurement into a vanilla dictionary.
        """

        return {
            'totalMeasured': self.total_measured,
            'totalCovered': self.total_covered,
        }

    @staticmethod
    def from_dict(input_dictionary):
        """
        Read the measurement in from the specified dictionary.
        """

        total_measured = input_dictionary["totalMeasured"]
        total_covered = input_dictionary["totalCovered"]
        return CoverageMeasurement(
            total_measured=total_measured, total_covered=total_covered,
        )


# pylint: disable=too-many-instance-attributes
class CoverageTotals:
    """
    Class to contain information about coverage totals.
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        project_name=None,
        report_source=None,
        instruction_level=None,
        branch_level=None,
        line_level=None,
        complexity_level=None,
        method_level=None,
        class_level=None,
    ):
        self.project_name = project_name
        self.report_source = report_source
        self.instruction_level = instruction_level
        self.branch_level = branch_level
        self.line_level = line_level
        self.complexity_level = complexity_level
        self.method_level = method_level
        self.class_level = class_level

    # pylint: enable=too-many-arguments

    def __eq__(self, other):
        """
        Overrides the default implementation
        """
        if isinstance(other, CoverageTotals):
            return (
                self.project_name == other.project_name
                and self.report_source == other.report_source
                and self.instruction_level == other.instruction_level
                and self.branch_level == other.branch_level
                and self.line_level == other.line_level
                and self.complexity_level == other.complexity_level
                and self.method_level == other.method_level
                and self.class_level == other.class_level
            )
        return NotImplemented

    def to_dict(self):
        """
        Convert the current measurement into a vanilla dictionary.
        """

        serialized_dictionary = {
            'projectName': self.project_name,
            'reportSource': self.report_source,
        }

        if self.instruction_level:
            serialized_dictionary["instructionLevel"] = self.instruction_level.to_dict()
        if self.branch_level:
            serialized_dictionary["branchLevel"] = self.branch_level.to_dict()
        if self.line_level:
            serialized_dictionary["lineLevel"] = self.line_level.to_dict()
        if self.complexity_level:
            serialized_dictionary["complexityLevel"] = self.complexity_level.to_dict()
        if self.method_level:
            serialized_dictionary["methodLevel"] = self.method_level.to_dict()
        if self.class_level:
            serialized_dictionary["classLevel"] = self.class_level.to_dict()
        return serialized_dictionary

    @staticmethod
    def from_dict(input_dictionary):
        """
        Read the measurement in from the specified dictionary.
        """

        project_name = input_dictionary["projectName"]
        report_source = input_dictionary["reportSource"]
        instruction_level = None
        branch_level = None
        line_level = None
        complexity_level = None
        method_level = None
        class_level = None
        if "instructionLevel" in input_dictionary:
            instruction_level = CoverageMeasurement.from_dict(
                input_dictionary["instructionLevel"]
            )
        if "branchLevel" in input_dictionary:
            branch_level = CoverageMeasurement.from_dict(
                input_dictionary["branchLevel"]
            )
        if "lineLevel" in input_dictionary:
            line_level = CoverageMeasurement.from_dict(input_dictionary["lineLevel"])
        if "complexityLevel" in input_dictionary:
            complexity_level = CoverageMeasurement.from_dict(
                input_dictionary["complexityLevel"]
            )
        if "methodLevel" in input_dictionary:
            method_level = CoverageMeasurement.from_dict(
                input_dictionary["methodLevel"]
            )
        if "classLevel" in input_dictionary:
            class_level = CoverageMeasurement.from_dict(input_dictionary["classLevel"])
        return CoverageTotals(
            project_name=project_name,
            report_source=report_source,
            instruction_level=instruction_level,
            branch_level=branch_level,
            line_level=line_level,
            complexity_level=complexity_level,
            method_level=method_level,
            class_level=class_level,
        )

"""
Module to provide an encapsulation of the test totals.
"""

from typing import Any, Dict, Optional

from project_summarizer.plugins.test_measurement import TestMeasurement


class TestTotals:
    """
    Class to provide an encapsulation of the test totals.
    """

    __test__ = False

    def __init__(
        self, project_name: Optional[str] = None, report_source: Optional[str] = None
    ) -> None:
        self.project_name = project_name
        self.report_source = report_source
        self.measurements: Dict[str, TestMeasurement] = {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the current totals into a vanilla dictionary.
        """

        serialized_dictionary: Dict[str, Any] = {
            "projectName": self.project_name,
            "reportSource": self.report_source,
        }

        measurements_array = [
            next_measurement.to_dict()
            for _, next_measurement in self.measurements.items()
        ]

        measurements_array.sort(key=lambda item: item["name"])

        serialized_dictionary["measurements"] = measurements_array
        return serialized_dictionary

    @staticmethod
    def from_dict(input_dictionary: Dict[str, Any]) -> "TestTotals":
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

"""
Module to test the classes for the coverage models.  This coverage is required
as the CoverageMeasurement class and the CoverageTotals class both implement
the _eq_ function.
"""
from project_summarizer.plugins.coverage_model import (
    CoverageMeasurement,
    CoverageTotals,
)


def test_coverage_totals_equal():
    """
    Test to make sure the coverage totals is equal to another total of the same amount.
    """

    # Arrange
    first_total = CoverageTotals(project_name="?", report_source="pytest")
    first_total.branch_level = CoverageMeasurement(total_covered=5, total_measured=10)
    first_total.line_level = CoverageMeasurement(total_covered=15, total_measured=20)

    second_total = CoverageTotals(project_name="?", report_source="pytest")
    second_total.branch_level = CoverageMeasurement(total_covered=5, total_measured=10)
    second_total.line_level = CoverageMeasurement(total_covered=15, total_measured=20)

    # Act
    actual_result = bool(first_total == second_total)

    # Assert
    assert actual_result


def test_coverage_totals_not_equal():
    """
    Test to make sure the coverage totals is not equal to another total of almost the same amount.
    """

    # Arrange
    first_line_coverage_measured = 20
    second_line_coverage_measured = 21

    first_total = CoverageTotals(project_name="?", report_source="pytest")
    first_total.branch_level = CoverageMeasurement(total_covered=5, total_measured=10)
    first_total.line_level = CoverageMeasurement(
        total_covered=15, total_measured=first_line_coverage_measured
    )

    second_total = CoverageTotals(project_name="?", report_source="pytest")
    second_total.branch_level = CoverageMeasurement(total_covered=5, total_measured=10)
    second_total.line_level = CoverageMeasurement(
        total_covered=15, total_measured=second_line_coverage_measured
    )

    # Act
    actual_result = bool(first_total == second_total)

    # Assert
    assert not actual_result


def test_coverage_totals_not_equal_different_object():
    """
    Test to make sure the coverage totals is not equal to another object that is not a total object.
    """

    # Arrange
    first_total = CoverageTotals(project_name="?", report_source="pytest")
    first_total.branch_level = CoverageMeasurement(total_covered=5, total_measured=10)
    first_total.line_level = CoverageMeasurement(total_covered=15, total_measured=20)

    # Act
    actual_result = bool(first_total == "second_total")

    # Assert
    assert not actual_result


def test_coverage_measurements_equal():
    """
    Test to make sure the coverage measurements is equal to another measurement of the same amount.
    """

    # Arrange
    first_measurement = CoverageMeasurement(total_covered=5, total_measured=10)

    second_measurement = CoverageMeasurement(total_covered=5, total_measured=10)

    # Act
    actual_result = bool(first_measurement == second_measurement)

    # Assert
    assert actual_result


def test_coverage_measurements_not_equal():
    """
    Test to make sure the coverage measurements is not equal to another measurement of almost the same amount.
    """

    # Arrange
    first_total_measurement = 20
    second_total_measurement = 21

    first_measurement = CoverageMeasurement(
        total_covered=5, total_measured=first_total_measurement
    )

    second_measurement = CoverageMeasurement(
        total_covered=5, total_measured=second_total_measurement
    )

    # Act
    actual_result = bool(first_measurement == second_measurement)

    # Assert
    assert not actual_result


def test_coverage_measurement_not_equal_different_object():
    """
    Test to make sure the coverage measurements is not equal to another object that is not a total object.
    """

    # Arrange
    first_measurement = CoverageMeasurement(total_covered=5, total_measured=10)

    # Act
    actual_result = bool(first_measurement == "second_measurement")

    # Assert
    assert not actual_result

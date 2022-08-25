"""
Module to test the various profiles seen with various coverage tools.
"""
from project_summarizer.plugins.coverage_model import (
    CoverageMeasurement,
    CoverageTotals,
)


def test_pytest_cobertura_profile():
    """
    Test to make sure the model handles the cobertura profile used by pytest.
    """

    # Arrange
    coverage_profile = CoverageTotals(project_name="?", report_source="pytest")
    coverage_profile.branch_level = CoverageMeasurement(
        total_covered=5, total_measured=10
    )
    coverage_profile.line_level = CoverageMeasurement(
        total_covered=15, total_measured=20
    )

    g_branch = {"totalCovered": 5, "totalMeasured": 10}
    g_line = {"totalCovered": 15, "totalMeasured": 20}
    expected_dictionary = {
        "projectName": "?",
        "reportSource": "pytest",
        "branchLevel": g_branch,
        "lineLevel": g_line,
    }

    # Act
    coverage_profile_as_dictionary = coverage_profile.to_dict()
    back_from_dictionary = CoverageTotals.from_dict(coverage_profile_as_dictionary)

    # Assert
    assert coverage_profile_as_dictionary == expected_dictionary
    assert back_from_dictionary == coverage_profile


def test_junit_jacoco_profile():
    """
    Test to make sure the model handles the jacoco profile used by junit.
    """

    # Arrange
    coverage_profile = CoverageTotals(project_name="?", report_source="junit")
    coverage_profile.instruction_level = CoverageMeasurement(
        total_covered=25, total_measured=30
    )
    coverage_profile.line_level = CoverageMeasurement(
        total_covered=15, total_measured=20
    )
    coverage_profile.branch_level = CoverageMeasurement(
        total_covered=5, total_measured=10
    )
    coverage_profile.complexity_level = CoverageMeasurement(
        total_covered=6, total_measured=11
    )
    coverage_profile.method_level = CoverageMeasurement(
        total_covered=3, total_measured=4
    )
    coverage_profile.class_level = CoverageMeasurement(
        total_covered=1, total_measured=1
    )

    g_instructions = {"totalCovered": 25, "totalMeasured": 30}
    g_line = {"totalCovered": 15, "totalMeasured": 20}
    g_branch = {"totalCovered": 5, "totalMeasured": 10}
    g_complexity = {"totalCovered": 6, "totalMeasured": 11}
    g_method = {"totalCovered": 3, "totalMeasured": 4}
    g_class = {"totalCovered": 1, "totalMeasured": 1}
    expected_dictionary = {
        "projectName": "?",
        "reportSource": "junit",
        "instructionLevel": g_instructions,
        "lineLevel": g_line,
        "branchLevel": g_branch,
        "complexityLevel": g_complexity,
        "methodLevel": g_method,
        "classLevel": g_class,
    }

    # Act
    coverage_profile_as_dictionary = coverage_profile.to_dict()
    back_from_dictionary = CoverageTotals.from_dict(coverage_profile_as_dictionary)

    # Assert
    assert coverage_profile_as_dictionary == expected_dictionary
    assert back_from_dictionary == coverage_profile


def test_made_up_profile():
    """
    Test to make sure the model can test a fictional profile that does not have
    any line or branch measurements, say a coverage of assembly instructions.
    """

    # Arrange
    coverage_profile = CoverageTotals(project_name="?", report_source="asmunit")
    coverage_profile.instruction_level = CoverageMeasurement(
        total_covered=25, total_measured=30
    )

    g_instructions = {"totalCovered": 25, "totalMeasured": 30}
    expected_dictionary = {
        "projectName": "?",
        "reportSource": "asmunit",
        "instructionLevel": g_instructions,
    }

    # Act
    coverage_profile_as_dictionary = coverage_profile.to_dict()
    back_from_dictionary = CoverageTotals.from_dict(coverage_profile_as_dictionary)

    # Assert
    assert coverage_profile_as_dictionary == expected_dictionary
    assert back_from_dictionary == coverage_profile

"""
Module to test the various profiles seen with various coverage tools.
"""
from pyscan.model import CoverageMeasurement, CoverageTotals


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

    expected_dictionary = {}
    expected_dictionary["projectName"] = "?"
    expected_dictionary["reportSource"] = "pytest"

    g_branch = {}
    g_branch["totalCovered"] = 5
    g_branch["totalMeasured"] = 10
    g_line = {}
    g_line["totalCovered"] = 15
    g_line["totalMeasured"] = 20

    expected_dictionary["branchLevel"] = g_branch
    expected_dictionary["lineLevel"] = g_line

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

    expected_dictionary = {}
    expected_dictionary["projectName"] = "?"
    expected_dictionary["reportSource"] = "junit"

    g_instructions = {}
    g_instructions["totalCovered"] = 25
    g_instructions["totalMeasured"] = 30
    g_line = {}
    g_line["totalCovered"] = 15
    g_line["totalMeasured"] = 20
    g_branch = {}
    g_branch["totalCovered"] = 5
    g_branch["totalMeasured"] = 10
    g_complexity = {}
    g_complexity["totalCovered"] = 6
    g_complexity["totalMeasured"] = 11
    g_method = {}
    g_method["totalCovered"] = 3
    g_method["totalMeasured"] = 4
    g_class = {}
    g_class["totalCovered"] = 1
    g_class["totalMeasured"] = 1

    expected_dictionary["instructionLevel"] = g_instructions
    expected_dictionary["lineLevel"] = g_line
    expected_dictionary["branchLevel"] = g_branch
    expected_dictionary["complexityLevel"] = g_complexity
    expected_dictionary["methodLevel"] = g_method
    expected_dictionary["classLevel"] = g_class

    # Act
    coverage_profile_as_dictionary = coverage_profile.to_dict()
    back_from_dictionary = CoverageTotals.from_dict(coverage_profile_as_dictionary)

    # Assert
    assert coverage_profile_as_dictionary == expected_dictionary
    assert back_from_dictionary == coverage_profile

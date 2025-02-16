"""
Module to provide for "-m project_summarizer" access to the module,
as if it was run from the console.
"""

from project_summarizer.main import ProjectSummarizer


def main() -> None:
    """
    Main entry point.  Exposed in this manner so that the setup
    entry_points configuration has something to execute.
    """
    ProjectSummarizer().main()


if __name__ == "__main__":
    main()

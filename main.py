"""
Module to provide for a simple bootstrap for the project.
"""

from project_summarizer.main import ProjectSummarizer


class Main:
    """
    Class to provide for a simple bootstrap for the project.
    """

    def main(self):
        """
        Main entrance point.
        """
        ProjectSummarizer().main()


if __name__ == "__main__":
    Main().main()

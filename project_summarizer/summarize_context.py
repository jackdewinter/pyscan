"""
Module to hold the context to be passed to the summarizers.
"""
import os


class SummarizeContext:
    """
    Class to hold the context to be passed to the summarizers.
    """

    def __init__(self, report_dir: str, publish_dir: str) -> None:
        self.__report_dir = report_dir
        self.__publish_dir = publish_dir

    @property
    def report_dir(self) -> str:
        """
        Directory used to create report summaries in.
        """
        return self.__report_dir

    @property
    def publish_dir(self) -> str:
        """
        Directory used to publish summaries to.
        """
        return self.__publish_dir

    def compute_published_path_to_file(self, file_to_publish: str) -> str:
        """
        Compute the path for the given file, assuming it will be placed in the publish directory.
        """

        return os.path.join(
            self.__publish_dir,
            os.path.basename(file_to_publish),
        )

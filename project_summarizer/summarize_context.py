"""
Module to hold the context to be passed to the summarizers.
"""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class SummarizeContext:
    """
    Class to hold the context to be passed to the summarizers.
    """

    report_dir: str
    publish_dir: str

    def compute_published_path_to_file(self, file_to_publish: str) -> str:
        """
        Compute the path for the given file, assuming it will be placed in the publish directory.
        """

        return os.path.join(
            self.publish_dir,
            os.path.basename(file_to_publish),
        )

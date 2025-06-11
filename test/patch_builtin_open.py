"""
Module to patch the "builtin.open" function.
"""

import unittest.mock
from typing import Any, Dict, List, Optional, Tuple, Union, cast


class PatchBuiltinOpen:
    """
    Class to patch the "builtin.open" function.
    """

    # pylint: disable=no-member
    def __init__(self) -> None:
        self.mock_patcher: Optional[unittest.mock._patch_default_new] = None
        self.patched_open: Optional[
            Union[unittest.mock.MagicMock, unittest.mock.AsyncMock]
        ] = None
        self.open_file_args: List[Any] = []
        self.content_map: Dict[str, str] = {}
        self.exception_map: Dict[str, Tuple[str, Optional[str]]] = {}

    # pylint: enable=no-member

    def start(self) -> None:
        """
        Start the patching of the "open" function.
        """
        self.mock_patcher = unittest.mock.patch("builtins.open")
        self.patched_open = self.mock_patcher.start()
        self.patched_open.side_effect = self.my_open
        self.open_file_args = [f"map={str(self.exception_map)}"]

    def stop(self) -> None:
        """
        Stop the patching of the "open" function.
        """
        if self.mock_patcher:
            self.mock_patcher.stop()
        self.mock_patcher = None

    def register_text_content(self, exact_file_name: str, file_contents: str) -> None:
        """
        Register text content to return when the specified file is opened for reading as
        a test file.
        """
        self.content_map[exact_file_name] = file_contents

    def register_exception(
        self,
        exact_file_name: str,
        file_mode: str,
        exception_message: Optional[str] = None,
    ) -> None:
        """
        Register an exception to raise when the specified file is opened with the given mode.
        """
        self.exception_map[exact_file_name] = (file_mode, exception_message)

    # pylint: disable=unspecified-encoding
    def my_open(self, *args: List[Any], **kwargs: Dict[str, Any]) -> Any:
        """
        Provide alternate handling of the "builtins.open" function.
        """
        filename = cast(str, args[0])
        filemode = cast(str, args[1] if len(args) > 1 else "r")
        if filename in self.content_map and filemode == "r":
            self.open_file_args.append((args, "text-content"))
            content = self.content_map[filename]

            file_object = unittest.mock.mock_open(read_data=content).return_value
            file_object.__iter__.return_value = content.splitlines(True)
            return file_object

        if filename in self.exception_map:
            match_filemode, exception_message = self.exception_map[filename]
            if filemode == match_filemode:
                self.open_file_args.append((args, "exception-raised"))
                raise IOError(exception_message)
            self.open_file_args.append((args, "exception-mode-mismatch"))

        assert self.mock_patcher is not None, "Patch not started"
        self.mock_patcher.stop()
        try:
            self.open_file_args.append((args, "passthrough"))
            return open(  # type: ignore
                filename,
                filemode,
                **kwargs,
            )
        finally:
            self.patched_open = self.mock_patcher.start()
            self.patched_open.side_effect = self.my_open

    # pylint: enable=unspecified-encoding

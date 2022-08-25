"""
Module to allow for a critical error within a plugin to be encapsulated
and reported.
"""

from typing import Optional


class BadPluginError(Exception):
    """
    Class to allow for a critical error within a plugin to be encapsulated
    and reported.
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        file_name: Optional[str] = None,
        class_name: Optional[str] = None,
        field_name: Optional[str] = None,
        is_constructor: bool = False,
        is_empty: bool = False,
        formatted_message: Optional[str] = None,
    ) -> None:
        if not formatted_message and file_name:
            formatted_message = BadPluginError.__create_file_name_message(
                file_name, class_name, is_constructor
            )
        elif class_name:
            formatted_message = BadPluginError.__create_class_name_message(
                class_name, formatted_message, field_name, is_empty
            )
        super().__init__(formatted_message)

    # pylint: enable=too-many-arguments

    @staticmethod
    def __create_file_name_message(
        file_name: Optional[str], class_name: Optional[str], is_constructor: bool
    ) -> str:
        if class_name:
            return (
                f"Plugin file named '{file_name}' threw an exception in the constructor for the class '{class_name}'."
                if is_constructor
                else f"Plugin file named '{file_name}' does not contain a class named '{class_name}'."
            )

        return f"Plugin file named '{file_name}' cannot be loaded."

    @staticmethod
    def __create_class_name_message(
        class_name: Optional[str],
        formatted_message: Optional[str],
        field_name: Optional[str],
        is_empty: bool,
    ) -> str:
        if formatted_message:
            return f"Plugin class '{class_name}' had a critical failure: {formatted_message}"
        if field_name:
            return (
                f"Plugin class '{class_name}' returned an empty value for field name '{field_name}'."
                if is_empty
                else f"Plugin class '{class_name}' returned an improperly typed value for field name '{field_name}'."
            )
        return f"Plugin class '{class_name}' had a critical failure loading the plugin details."

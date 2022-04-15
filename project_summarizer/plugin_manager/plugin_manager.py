"""
Module to take care of managing the plugins.
"""

import argparse
import importlib
import importlib.machinery
import os
import sys
from importlib.util import module_from_spec
from typing import Any, Dict, List, Tuple, cast

from project_summarizer.plugin_manager.bad_plugin_error import BadPluginError
from project_summarizer.plugin_manager.plugin_details import PluginDetails
from project_summarizer.plugin_manager.project_summarizer_plugin import (
    ProjectSummarizerPlugin,
)
from project_summarizer.summarize_context import SummarizeContext


class PluginManager:
    """
    Class to take care of managing the plugins.
    """

    def __init__(self) -> None:
        self.__available_plugins: List[ProjectSummarizerPlugin] = []
        self.__plugin_argument_names: Dict[str, ProjectSummarizerPlugin] = {}
        self.__plugin_variable_names: Dict[str, str] = {}
        self.__loaded_classes: List[
            Tuple[ProjectSummarizerPlugin, str, PluginDetails]
        ] = []

    def initialize_plugins(self) -> List[str]:
        """
        Initialize all the plugins.
        """

        remaining_arguments: List[str] = []
        self.__available_plugins = []

        base_plugin_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "..", "plugins"
        )

        remaining_arguments = sys.argv[1:]
        additional_plugins_to_load = [
            os.path.join(base_plugin_path, "cobertura_plugin.py"),
            os.path.join(base_plugin_path, "junit_plugin.py"),
        ]
        # print(f"remaining_arguments>>{str(remaining_arguments)}")
        while remaining_arguments:
            last_args = remaining_arguments[:]
            parser = argparse.ArgumentParser(allow_abbrev=False, add_help=False)
            PluginManager.add_plugin_arguments(parser)
            known_args = parser.parse_known_args(args=remaining_arguments)
            if known_args[0].add_plugin:
                additional_plugins_to_load.extend(known_args[0].add_plugin)
            remaining_arguments = known_args[1]
            if len(last_args) == len(remaining_arguments):
                break
        # print(f"remaining_arguments>>{str(remaining_arguments)}")
        # print("additional_plugins_to_load>>" + str(additional_plugins_to_load))
        self.__load_plugins(additional_plugins_to_load)

        return remaining_arguments

    @staticmethod
    def add_plugin_arguments(parser: argparse.ArgumentParser) -> None:
        """
        Add the argument to allow for pluings to be added.
        """
        parser.add_argument(
            "--add-plugin",
            dest="add_plugin",
            action="append",
            help="Add a plugin file to provide additional project summaries.",
        )

    def add_command_line_arguments_for_plugins(
        self, parser: argparse.ArgumentParser
    ) -> None:
        """
        Add the command line arguments for each plugin to the argument parser.
        """
        for next_plugin_instance in self.__available_plugins:
            try:
                (
                    plugin_argument_name,
                    plugin_variable_name,
                ) = next_plugin_instance.add_command_line_arguments(parser)
            except Exception as this_exception:
                raise BadPluginError(
                    class_name=type(next_plugin_instance).__name__,
                    formatted_message="Bad Plugin Error calling add_command_line_arguments.",
                ) from this_exception

            self.__plugin_argument_names[plugin_argument_name] = next_plugin_instance
            self.__plugin_variable_names[plugin_argument_name] = plugin_variable_name

    def __attempt_to_load_plugin(
        self, next_plugin_module: str, plugin_class_name: str, next_plugin_file: str
    ) -> None:
        """
        Attempt to cleanly load the specified plugin.
        """
        if not os.path.exists(next_plugin_file):
            raise BadPluginError(
                formatted_message=f"Plugin file '{next_plugin_file}' does not exist."
            )
        # https://www.blog.pythonlibrary.org/2016/05/27/python-201-an-intro-to-importlib/
        try:
            next_plugin_file = os.path.abspath(next_plugin_file)
            next_plugin_file_directory = os.path.dirname(next_plugin_file)
            os.chdir(next_plugin_file_directory)
            # print(f"cd={os.getcwd()}")

            # print(f"module:>>{next_plugin_module}")
            # print(f"class:>>{plugin_class_name}")
            # print(f"file:>>{next_plugin_file}")
            loader = importlib.machinery.SourceFileLoader(
                next_plugin_module, next_plugin_file
            )
            # print(f"loader={loader}")
            module_specification = importlib.util.spec_from_loader(
                next_plugin_module, loader
            )
            assert module_specification is not None
            assert module_specification.loader is not None
            # print(f"module_specification={module_specification}")
            module_type = module_from_spec(module_specification)
            # print(f"module_type={module_type}")
            module_specification.loader.exec_module(module_type)
            # print("module_loaded")
        except Exception as this_exception:
            # print(type(this_exception))
            # print(this_exception)
            raise BadPluginError(file_name=next_plugin_file) from this_exception

        # print(f">>{next_plugin_module}")
        if not hasattr(module_type, plugin_class_name):
            raise BadPluginError(
                file_name=next_plugin_file, class_name=plugin_class_name
            ) from None
        my_class = getattr(module_type, plugin_class_name)

        try:
            plugin_class_instance = cast(ProjectSummarizerPlugin, my_class())
        except Exception as this_exception:
            raise BadPluginError(
                file_name=next_plugin_file,
                class_name=plugin_class_name,
                is_constructor=True,
            ) from this_exception

        plugin_details = self.__load_details(
            plugin_class_instance, plugin_class_name, next_plugin_file
        )

        # print(f"__loaded_classes>>{self.__loaded_classes}")
        self.__loaded_classes.append(
            (plugin_class_instance, next_plugin_file, plugin_details)
        )
        self.__available_plugins.append(plugin_class_instance)
        # print(f"__loaded_classes>>{self.__loaded_classes}")

    @classmethod
    def __verify_string_field(
        cls, plugin_instance: ProjectSummarizerPlugin, field_name: str, field_value: Any
    ) -> None:
        """
        Verify that the detail field is a valid string.
        """

        if not isinstance(field_value, str):
            raise BadPluginError(
                class_name=type(plugin_instance).__name__, field_name=field_name
            )
        if not field_value:
            raise BadPluginError(
                class_name=type(plugin_instance).__name__,
                field_name=field_name,
                is_empty=True,
            )

    @classmethod
    def __verify_integer_field(
        cls, plugin_instance: ProjectSummarizerPlugin, field_name: str, field_value: Any
    ) -> None:
        """
        Verify that the detail field is a valid integer.
        """

        if not isinstance(field_value, int):
            raise BadPluginError(
                class_name=type(plugin_instance).__name__, field_name=field_name
            )

    def __load_details(
        self,
        plugin_class_instance: ProjectSummarizerPlugin,
        plugin_class_name: str,
        instance_file_name: str,
    ) -> PluginDetails:

        try:
            found_details = plugin_class_instance.get_details()
        except Exception as this_exception:
            raise BadPluginError(
                class_name=plugin_class_name,
            ) from this_exception

        self.__verify_string_field(
            plugin_class_instance, "plugin_id", found_details.plugin_id
        )
        self.__verify_string_field(
            plugin_class_instance, "plugin_name", found_details.plugin_name
        )
        self.__verify_string_field(
            plugin_class_instance, "plugin_version", found_details.plugin_version
        )
        self.__verify_integer_field(
            plugin_class_instance,
            "plugin_interface_version",
            found_details.plugin_interface_version,
        )

        if found_details.plugin_interface_version != 1:
            raise BadPluginError(
                formatted_message=f"Plugin '{instance_file_name}' with an interface version "
                + f"('{found_details.plugin_interface_version}') that is not '1'."
            )
        return found_details

    @classmethod
    def __snake_to_camel(cls, word: str) -> str:
        return "".join(x.capitalize() or "_" for x in word.split("_"))

    def __load_plugins(self, plugin_files: List[str]) -> None:
        """
        Given an array of additional plugins, load them into the global namespace.
        """
        old_directory = os.getcwd()
        try:
            for next_plugin_file in plugin_files:
                file_base_name = os.path.basename(next_plugin_file)
                next_plugin_module = (
                    file_base_name[:-3]
                    if file_base_name.endswith(".py")
                    else file_base_name
                )
                plugin_class_name = self.__snake_to_camel(next_plugin_module)
                self.__attempt_to_load_plugin(
                    next_plugin_module, plugin_class_name, next_plugin_file
                )
        finally:
            os.chdir(old_directory)

    def set_context(self, context: SummarizeContext) -> None:
        """
        Set the context for each plugin.
        """
        for next_plugin in self.__available_plugins:
            try:
                next_plugin.set_context(context)
            except Exception as this_exception:
                raise BadPluginError(
                    class_name=type(next_plugin).__name__,
                    formatted_message="Bad Plugin Error calling set_context.",
                ) from this_exception

    def generate_report(
        self,
        next_command_line_argument: str,
        arguments_as_dictionary: Dict[str, Any],
        column_width: int,
        args: argparse.Namespace,
    ) -> None:
        """
        Generate the reports for the plugins.
        """
        if next_command_line_argument in self.__plugin_argument_names:
            plugin_instance = self.__plugin_argument_names[next_command_line_argument]
            plugin_variable_name = self.__plugin_variable_names[
                next_command_line_argument
            ]
            try:
                plugin_instance.generate_report(
                    args.only_changes,
                    column_width,
                    arguments_as_dictionary[plugin_variable_name],
                )
            except Exception as this_exception:
                raise BadPluginError(
                    class_name=type(plugin_instance).__name__,
                    formatted_message="Bad Plugin Error calling generate_report.",
                ) from this_exception

    def get_output_paths(self) -> List[str]:
        """
        Create a collection of all paths for the existing plugins.
        """
        valid_paths = []
        for plugin_instance in self.__available_plugins:
            try:
                plugin_output_path = plugin_instance.get_output_path()
            except Exception as this_exception:
                raise BadPluginError(
                    class_name=type(plugin_instance).__name__,
                    formatted_message="Bad Plugin Error calling get_output_path.",
                ) from this_exception

            if os.path.exists(plugin_output_path) and not os.path.isfile(
                plugin_output_path
            ):
                raise BadPluginError(
                    formatted_message=f"Summary path '{plugin_output_path}' is not a file."
                )
            valid_paths.append(plugin_output_path)
        return valid_paths

    def find_any_plugins_arguments(self, args: argparse.Namespace) -> bool:
        """
        Determine if there are any plugin arguments in the remaining list of arguments.
        """
        are_plugin_arguments_present = False
        arguments_as_dictionary = vars(args)
        for next_plugin_argument in self.__plugin_argument_names:
            plugin_variable_name = self.__plugin_variable_names[next_plugin_argument]
            assert plugin_variable_name in arguments_as_dictionary
            argument_value = arguments_as_dictionary[plugin_variable_name]
            are_plugin_arguments_present = bool(argument_value.strip())
            if are_plugin_arguments_present:
                break
        return are_plugin_arguments_present

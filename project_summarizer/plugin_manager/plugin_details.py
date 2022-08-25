"""
Module to provide details about a plugin, supplied by the plugin.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PluginDetails:
    """
    Class to provide details about a plugin, supplied by the plugin.
    """

    plugin_id: str
    plugin_name: str
    plugin_version: str
    plugin_interface_version: int

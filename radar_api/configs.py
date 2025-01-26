# -----------------------------------------------------------------------------.
# MIT License

# Copyright (c) 2024 RADAR-API developers
#
# This file is part of RADAR-API.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# -----------------------------------------------------------------------------.
"""RADAR-API configurations settings."""
import os

from radar_api.utils.yaml import read_yaml, write_yaml


def _define_config_filepath():
    """Define the config YAML file path."""
    # Retrieve user home directory
    home_directory = os.path.expanduser("~")
    # Define path where .config_radar_api.yaml file should be located
    return os.path.join(home_directory, ".config_radar_api.yaml")


def define_configs(
    base_dir: str | None = None,
):
    """Defines the RADAR-API configuration file with the given credentials and base directory.

    Parameters
    ----------
    base_dir : str
        The base directory where radar data are stored.

    Notes
    -----
    This function writes a YAML file to the user's home directory at ~/.config_radar_api.yaml
    with the given RADAR-API credentials and base directory. The configuration file can be
    used for authentication when making RADAR-API requests.

    """
    # Define path to .config_radar_api.yaml file
    filepath = _define_config_filepath()

    # If the config exists, read it and update it ;)
    if os.path.exists(filepath):
        config_dict = read_yaml(filepath)
        action_msg = "updated"
    else:
        config_dict = {}
        action_msg = "written"

    # Add RADAR-API base directory
    if base_dir is not None:
        config_dict["base_dir"] = str(base_dir)  # deal with Pathlib

    # Write the RADAR-API config file
    write_yaml(config_dict, filepath, sort_keys=False)

    print(f"The RADAR-API config file has been {action_msg} successfully!")


def read_configs() -> dict[str, str]:
    """Reads the RADAR-API configuration file and returns a dictionary with the configuration settings.

    Returns
    -------
    dict
        A dictionary containing the configuration settings for the RADAR-API.

    Raises
    ------
    ValueError
        If the configuration file has not been defined yet. Use `radar_api.define_configs()` to
        specify the configuration file path and settings.

    Notes
    -----
    This function reads the YAML configuration file located at ~/.config_radar_api.yaml, which
    should contain the RADAR-API credentials and base directory specified by `radar_api.define_configs()`.

    """
    # Define path to .config_radar_api.yaml file
    filepath = _define_config_filepath()
    # Check it exists
    if not os.path.exists(filepath):
        raise ValueError(
            "The RADAR-API config file has not been specified. Use radar_api.define_configs to specify it !",
        )
    # Read the RADAR-API config file
    return read_yaml(filepath)


####--------------------------------------------------------------------------.
def _get_config_key(key):
    """Return the config key."""
    import radar_api

    value = radar_api.config.get(key, None)
    if value is None:
        raise ValueError(f"The '{key}' is not specified in the RADAR-API configuration file.")
    return value


def get_base_dir(base_dir=None):
    """Return the RADAR-API base directory."""
    import radar_api

    if base_dir is None:
        base_dir = radar_api.config.get("base_dir")
    if base_dir is None:
        raise ValueError("The 'base_dir' is not specified in the RADAR-API configuration file.")
    return str(base_dir)  # convert Path to str

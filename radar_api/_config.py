# -----------------------------------------------------------------------------.
# MIT License

# Copyright (c) 2025 RADAR-API developers
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
"""Donfig configuration utility.

See https://donfig.readthedocs.io/en/latest/configuration.html for more info.
"""

from donfig import Config

from radar_api.configs import read_configs


def _get_default_configs():
    """Retrieve the default RADAR-API settings from the ``.config_radar_api.yaml`` file."""
    try:
        config_dict = read_configs()
        config_dict = {key: value for key, value in config_dict.items() if value is not None}
    except Exception:
        config_dict = {}
    return config_dict


_CONFIG_DEFAULTS = {
    "base_dir": None,
}
_CONFIG_DEFAULTS.update(_get_default_configs())

_CONFIG_PATHS = []

config = Config("radar", defaults=[_CONFIG_DEFAULTS], paths=_CONFIG_PATHS)

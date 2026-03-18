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
"""RADAR-API Package."""

import contextlib
import os
from importlib.metadata import PackageNotFoundError, version

from radar_api._config import config
from radar_api.configs import (
    define_configs,
    read_configs,
)
from radar_api.download import download_files
from radar_api.info import group_filepaths
from radar_api.io import (
    available_networks,
    available_products,
    available_radars,
)
from radar_api.readers import (
    open_dataset,
    open_datatree,
    open_pyart,
)
from radar_api.search import find_files
from radar_api.utilities import (
    available_radars_around_point,
    available_radars_within_extent,
    read_database,
)

_root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


__all__ = [
    "available_networks",
    "available_products",
    "available_radars_around_point",
    "available_radars",
    "available_radars_within_extent",
    "config",
    "define_configs",
    "download_files",
    "find_files",
    "group_filepaths",
    "open_dataset",
    "open_datatree",
    "open_pyart",
    "read_configs",
    "read_database",
]

# Get version
with contextlib.suppress(PackageNotFoundError):
    __version__ = version("radar_api")

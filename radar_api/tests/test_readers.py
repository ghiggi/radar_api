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
"""This module test the RADAR-API readers functions."""
import os

import pyart
import pytest
import xarray as xr

import radar_api
from radar_api.readers import (
    check_software_availability,
    get_simplecache_file,
    open_dataset,
    open_datatree,
    open_pyart,
)


def test_get_simplecache_file():
    """Test file simple caching with fsspec."""
    filepath = "s3://noaa-nexrad-level2/2023/01/01/KABR/KABR20230101_000142_V06"
    file = get_simplecache_file(filepath)
    assert isinstance(file, str)


def test_check_software_availability_decorator():
    """Test check_software_availability_decorator raise ImportError."""

    @check_software_availability(software="dummy_package", conda_package="dummy_package")
    def dummy_function(a, b=1):
        return a, b

    with pytest.raises(ImportError):
        dummy_function()

    @check_software_availability(software="numpy", conda_package="numpy")
    def dummy_function(a, b=1):
        return a, b

    assert dummy_function(2, b=3) == (2, 3)


def test_open_datatree():
    """Test file with open_datatree."""
    network = "NEXRAD"
    filepath = os.path.join(radar_api._root_path, "radar_api", "tests", "test_data", "KABR20230101_000142_V06")
    dt = open_datatree(filepath, network=network)
    assert isinstance(dt, xr.DataTree)


def test_open_dataset():
    """Test file with open_dataset."""
    network = "NEXRAD"
    filepath = os.path.join(radar_api._root_path, "radar_api", "tests", "test_data", "KABR20230101_000142_V06")
    ds = open_dataset(filepath, sweep="sweep_0", network=network)
    assert isinstance(ds, xr.Dataset)


def test_open_pyart():
    """Test file with open_pyart."""
    network = "NEXRAD"
    filepath = os.path.join(radar_api._root_path, "radar_api", "tests", "test_data", "KABR20230101_000142_V06")
    radar_obj = open_pyart(filepath, network=network)
    assert isinstance(radar_obj, pyart.core.Radar)

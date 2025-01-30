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
"""This module defines file readers."""
import importlib
from functools import wraps

import fsspec

from radar_api.io import get_network_info


def get_simplecache_file(filepath):
    """Simple cache a s3 file."""
    file = fsspec.open_local(
        f"simplecache::{filepath}",  # assume filepath has s3://
        s3={"anon": True},
        filecache={"cache_storage": "."},
    )
    return file


def check_software_availability(software, conda_package):
    """A decorator to ensure that a software package is installed.

    Parameters
    ----------
    software : str
        The package name as recognized by Python's import system.
    conda_package : str
        The package name as recognized by conda-forge.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not importlib.util.find_spec(software):
                raise ImportError(
                    f"The '{software}' package is required but not found.\n"
                    "Please install it using conda:\n"
                    f"    conda install -c conda-forge {conda_package}",
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator


def get_xradar_datatree_reader(network):
    """Return the xradar datatree reader."""
    import xradar.io

    func = getattr(xradar.io, get_network_info(network)["xradar_reader"])
    return func


def get_pyart_reader(network):
    """Return the pyart reader."""
    import pyart.io

    try:
        func = getattr(pyart.io, get_network_info(network)["pyart_reader"])
    except AttributeError:
        func = getattr(pyart.aux_io, get_network_info(network)["pyart_reader"])
    return func


def get_xradar_engine(network):
    """Return the xradar engine."""
    return get_network_info(network)["xradar_engine"]


def _prepare_file(filepath):
    if filepath.startswith("s3"):
        filepath = get_simplecache_file(filepath)
    return filepath


@check_software_availability(software="xradar", conda_package="xradar")
def open_datatree(filepath, network, **kwargs):
    """Open a file into an xarray DataTree object using xradar."""
    filepath = _prepare_file(filepath)
    open_datatree = get_xradar_datatree_reader(network)
    dt = open_datatree(filepath, **kwargs)
    return dt


@check_software_availability(software="xradar", conda_package="xradar")
def open_dataset(filepath, network, sweep, **kwargs):
    """Open a file into an xarray Dataset object using xradar."""
    import xarray as xr

    filepath = _prepare_file(filepath)
    engine = get_xradar_engine(network)
    ds = xr.open_dataset(filepath, group=sweep, engine=engine, **kwargs)
    return ds


@check_software_availability(software="pyart", conda_package="arm_pyart")
def open_pyart(filepath, network, **kwargs):
    """Open a file into a pyart object."""
    filepath = _prepare_file(filepath)
    pyart_reader = get_pyart_reader(network)
    pyart_obj = pyart_reader(filepath, **kwargs)
    return pyart_obj

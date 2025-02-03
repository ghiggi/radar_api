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
"""This module provides functions for searching files on local disk and cloud buckets."""
import datetime

import pandas as pd
from trollsift import Parser

from radar_api.checks import (
    check_base_dir,
    check_network,
    check_protocol,
    check_radar,
    check_start_end_time,
)
from radar_api.configs import get_base_dir
from radar_api.filter import filter_files
from radar_api.io import get_bucket_prefix, get_directory_pattern, get_filesystem
from radar_api.utils.list import flatten_list

####--------------------------------------------------------------------------.


def get_pattern_shortest_time_component(directory_pattern):
    """Return the shortest time frequency component present in the pattern."""
    if "{time:%M}" in directory_pattern:
        return "min"
    if "{time:%H}" in directory_pattern:
        return "h"
    if any(s in directory_pattern for s in ["{time:%d}", "{time:%j}"]):
        return "D"
    if any(s in directory_pattern for s in ["{time:%m}", "{time:%b}", "{time:%B}"]):
        return "MS"
    if any(s in directory_pattern for s in ["{time:%Y}", "{time:%y}"]):
        return "Y"  # Y-DEC
    raise NotImplementedError


def get_list_timesteps(start_time, end_time, freq):
    """Return the list of timesteps (directory) to scan."""
    # Convert inputs to pandas Timestamps
    start = pd.to_datetime(start_time)
    end = pd.to_datetime(end_time)

    # Round start_time and end_time to the frequency resolution
    # "Y" --> set month and days to 01 and zero out hour, minute, second
    # "MS" --> set day to 01 and zero out hour, minute, second
    # "D" -> zero out hour, minute, second
    # "h" -> zero out minute, second
    # "min" -> zero out second
    if freq in ["D", "h", "min"]:
        timedelta = pd.Timedelta(1, freq)
        start = start - timedelta
        start = start.floor(freq)
        end = end.floor(freq)  # inclusive date range
        timedelta = pd.Timedelta(1, freq)
    elif freq == "MS":
        if start.month == 1:
            new_start_month = 12
            new_start_year = start.year - 1
        else:
            new_start_month = start.month - 1
            new_start_year = start.year
        start = pd.to_datetime(datetime.datetime(new_start_year, new_start_month, 1))
        end = pd.to_datetime(datetime.datetime(end.year, end.month, 1))
    elif freq == "Y":  # Y-DEC
        start = pd.to_datetime(datetime.datetime(start.year - 1, 1, 1))
        end = pd.to_datetime(datetime.datetime(end.year, 12, 31))
    else:
        raise NotImplementedError

    # Define timesteps (directory) to visit
    # - We search also in the previous directory for hour/day files spanning the directory boundary
    timesteps = pd.date_range(start=start, end=end, freq=freq, inclusive="both")
    return timesteps


def get_directories_paths(start_time, end_time, network, radar, protocol, base_dir):
    """Returns a list of the directory paths to scan."""
    # Get directory pattern
    directory_pattern = get_directory_pattern(protocol, network)
    # Identify frequency
    freq = get_pattern_shortest_time_component(directory_pattern)
    # Create list of time directories
    list_time = get_list_timesteps(start_time=start_time, end_time=end_time, freq=freq)
    # Compose directories path
    parser = Parser(directory_pattern)
    paths = [parser.compose({"time": time, "radar": radar, "base_dir": base_dir}) for time in list_time]
    return paths


def _try_list_files(fs, dir_path):
    try:
        fpaths = fs.ls(dir_path)
    except Exception:
        fpaths = []
    return fpaths


def find_files(
    radar,
    network,
    start_time,
    end_time,
    base_dir=None,
    protocol="s3",
    fs_args={},
    verbose=False,
):
    """
    Retrieve files from local or cloud bucket storage.

    Parameters
    ----------
    base_dir : str, optional
        This argument must be specified only if searching files on the local storage
        when protocol="file".
        It represents the path to the local directory where to search for radar data.
        If protocol="file" and base_dir is None, base_dir is retrieved from
        the RADAR-API config file.
        The default is None.
    protocol : str (optional)
        String specifying the location where to search for the data.
        If protocol="file", it searches on local storage (indicated by base_dir).
        Otherwise, protocol refers to a specific cloud bucket storage.
        Use `radar_api.available_protocols()` to check the available protocols.
        The default is "s3".
    fs_args : dict, optional
        Dictionary specifying optional settings to initiate the fsspec.filesystem.
        The default is an empty dictionary. Anonymous connection is set by default.
    radar : str
        The name of the radar.
        Use `radar_api.available_radars()` to retrieve the available satellites.
    network : str
        The name of the radar network.
        See `radar_api.available_network()` for available radar networks.
    start_time : datetime.datetime
        The start (inclusive) time of the interval period for retrieving the filepaths.
    end_time : datetime.datetime
        The end (exclusive) time of the interval period for retrieving the filepaths.
    verbose : bool, optional
        If True, it print some information concerning the file search.
        The default is False.
    """
    # Check inputs
    if protocol not in ["file", "local"] and base_dir is not None:
        raise ValueError("If protocol is not 'file' or 'local', base_dir must not be specified !")

    # Check for when searching on local storage
    if protocol in ["file", "local"]:
        # Get default local directory if base_dir = None
        base_dir = get_base_dir(base_dir)
        # Set protocol and fs_args expected by fsspec
        protocol = "file"
        fs_args = {}

    # -------------------------------------------------------------------------.
    # Format inputs
    protocol = check_protocol(protocol)
    base_dir = check_base_dir(base_dir)
    network = check_network(network)
    radar = check_radar(radar=radar, network=network)
    start_time, end_time = check_start_end_time(start_time, end_time)

    # Get filesystem
    fs = get_filesystem(protocol=protocol, fs_args=fs_args)
    bucket_prefix = get_bucket_prefix(protocol)

    # Get list of directories over which to search
    dir_paths = get_directories_paths(
        start_time=start_time,
        end_time=end_time,
        network=network,
        radar=radar,
        protocol=protocol,
        base_dir=base_dir,
    )

    # Report over how many directory to scan
    n_directories = len(dir_paths)
    if verbose:
        print(f"Searching files across {n_directories} directories.")

    # Loop over each directory:
    list_fpaths = []
    # dir_path = dir_paths[0]
    for dir_path in dir_paths:
        # Retrieve list of files
        fpaths = _try_list_files(fs=fs, dir_path=dir_path)
        # Special conditions
        if network == "NEXRAD":
            fpaths = [
                fpath for fpath in fpaths if "NWS_NEXRAD" not in fpath
            ]  # NWS_NEXRAD_NXL2DP or NWS_NEXRAD_NXL2LG tar balls
            fpaths = [fpath for fpath in fpaths if not fpath.endswith(".001")]  # repeated files
            fpaths = [fpath for fpath in fpaths if not fpath.endswith(".Z")]  # corrupted compressed files
            fpaths = [fpath for fpath in fpaths if not fpath.endswith("_MDM")]
        # Add bucket prefix
        fpaths = [bucket_prefix + fpath for fpath in fpaths]
        # Filter files if necessary
        fpaths = filter_files(fpaths, network=network, start_time=start_time, end_time=end_time)
        list_fpaths += fpaths

    # Flat the list of filepaths and return it
    return sorted(flatten_list(list_fpaths))

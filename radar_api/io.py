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
"""Define filesystems, buckets, connection types and directory structures."""
import datetime
import importlib
import os
import sys
from functools import wraps

import fsspec

from radar_api.checks import check_network, check_start_end_time
from radar_api.utils.list import flatten_list
from radar_api.utils.yaml import read_yaml


def get_network_config_path():
    from radar_api import _root_path

    path = os.path.join(_root_path, "radar_api", "etc", "network")
    return path


def get_network_radars_config_path(network):
    from radar_api import _root_path

    path = os.path.join(_root_path, "radar_api", "etc", "radar", network)
    return path


def get_network_config_filepath(network):
    filepath = os.path.join(get_network_config_path(), f"{network}.yaml")
    return filepath


def get_radar_config_filepath(network, radar):
    filepath = os.path.join(get_network_radars_config_path(network), f"{radar}.yaml")
    return filepath


def available_networks():
    network_config_path = get_network_config_path()
    networks_config_filenames = os.listdir(network_config_path)
    networks = [fname.split(".")[0] for fname in networks_config_filenames]
    return sorted(networks)


def _get_network_radars(network, start_time=None, end_time=None):
    radars_config_path = get_network_radars_config_path(network)
    radars_config_filenames = os.listdir(radars_config_path)
    radars = [fname.split(".")[0] for fname in radars_config_filenames]
    radars = [
        radar
        for radar in radars
        if is_radar_available(network=network, radar=radar, start_time=start_time, end_time=end_time)
    ]
    return radars


def available_radars(network=None, start_time=None, end_time=None):
    if network is None:
        networks = available_networks()
        list_radars = [
            _get_network_radars(network=network, start_time=start_time, end_time=end_time) for network in networks
        ]
        radars = flatten_list(list_radars)
    else:
        network = check_network(network)
        radars = _get_network_radars(network=network, start_time=start_time, end_time=end_time)

    return sorted(radars)


def get_network_info(network):
    network_config_path = get_network_config_filepath(network)
    info_dict = read_yaml(network_config_path)
    return info_dict


def get_xradar_datatree_reader(network):
    import xradar.io

    func = getattr(xradar.io, get_network_info(network)["xradar_reader"])
    return func


def get_pyart_reader(network):
    import pyart.io

    try:
        func = getattr(pyart.io, get_network_info(network)["pyart_reader"])
    except AttributeError:
        func = getattr(pyart.aux_io, get_network_info(network)["pyart_reader"])
    return func


def get_xradar_engine(network):
    return get_network_info(network)["xradar_engine"]


def get_radar_info(network, radar):
    network_config_path = get_radar_config_filepath(network, radar)
    info_dict = read_yaml(network_config_path)
    return info_dict


def get_current_utc_time():
    if sys.version_info >= (3, 11):
        return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    return datetime.datetime.utcnow()


def get_radar_time_coverage(network, radar):
    info_dict = get_radar_info(network=network, radar=radar)
    if "start_time" not in info_dict or "end_time" not in info_dict:
        raise ValueError(f"Time coverage information for {network} radar '{radar}' is unavailable.")
    start_time = info_dict["start_time"]
    end_time = info_dict["end_time"]
    start_time = datetime.datetime.fromisoformat(start_time)
    end_time = get_current_utc_time() if end_time == "" else datetime.datetime.fromisoformat(end_time)
    return start_time, end_time


def get_radar_start_time(network, radar):
    time_coverage = get_radar_time_coverage(network, radar)
    if time_coverage is not None:
        return time_coverage[0]
    return None


def get_radar_end_time(network, radar):
    time_coverage = get_radar_time_coverage(network, radar)
    if time_coverage is not None:
        return time_coverage[1]
    return None


def get_radar_location(network, radar):
    radar_info = get_radar_info(network=network, radar=radar)
    if "latitude" in radar_info and "longitude" in radar_info:
        return radar_info["longitude"], radar_info["latitude"]
    raise ValueError("Radar location not available.")


def is_radar_available(network, radar, start_time=None, end_time=None):
    """Check if a radar was existing within the specified time period.

    If ``start_time`` and ``end_time`` are ``None``, does not perform any check.

    Parameters
    ----------
    start_time : datetime.datetime, datetime.date, numpy.datetime64 or str
        Start time.
        Accepted types: ``datetime.datetime``, ``datetime.date``, ``numpy.datetime64`` or ``str``
        If string type, it expects the isoformat ``YYYY-MM-DD hh:mm:ss``.
    end_time : datetime.datetime, datetime.date, numpy.datetime64 or str
        Start time.
        Accepted types:  ``datetime.datetime``, ``datetime.date``, ``numpy.datetime64`` or ``str``
        If string type, it expects the isoformat ``YYYY-MM-DD hh:mm:ss``.
        If ``None``, assume current UTC time.

    """
    from radar_api.filter import is_file_within_time

    # Do not check if start_time and end_time not specified
    if start_time is None and end_time is None:
        return True

    # Initialize start_time and end_time
    if start_time is None:
        start_time = datetime.datetime(1987, 1, 1, 0, 0, 0)
    if end_time is None:
        end_time = get_current_utc_time()
    start_time, end_time = check_start_end_time(start_time, end_time)

    # Retrieve radar temporal coverage
    try:
        radar_start_time, radar_end_time = get_radar_time_coverage(network, radar)
    except Exception as e:
        print(str(e))
        return False

    # Verify if radar is available
    return is_file_within_time(
        start_time=start_time,
        end_time=end_time,
        file_start_time=radar_start_time,
        file_end_time=radar_end_time,
    )


def get_network_filename_patterns(network):
    return get_network_info(network)["filename_patterns"]


def get_directory_pattern(protocol, network):
    if protocol in ["s3", "gcs"]:
        directory_pattern = get_network_info(network)["cloud_directory_pattern"]
    else:
        directory_pattern = get_network_info(network)["local_directory_pattern"]
    return directory_pattern


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


def get_filesystem(protocol, fs_args={}):
    """
    Define fsspec filesystem.

    protocol : str
       String specifying the cloud bucket storage from which to retrieve
       the data. It must be specified if not searching data on local storage.
       Use `goes_api.available_protocols()` to retrieve available protocols.
    fs_args : dict, optional
       Dictionary specifying optional settings to initiate the fsspec.filesystem.
       The default is an empty dictionary. Anonymous connection is set by default.

    """
    if not isinstance(fs_args, dict):
        raise TypeError("fs_args must be a dictionary.")
    if protocol == "s3":
        # Set defaults
        # - Use the anonymous credentials to access public data
        _ = fs_args.setdefault("anon", True)  # TODO: or if is empty
        fs = fsspec.filesystem("s3", **fs_args)
        return fs
    if protocol == "gcs":
        # Set defaults
        # - Use the anonymous credentials to access public data
        _ = fs_args.setdefault("token", "anon")  # TODO: or if is empty
        fs = fsspec.filesystem("gcs", **fs_args)
        return fs
    if protocol in ["local", "file"]:
        fs = fsspec.filesystem("file")
        return fs
    raise NotImplementedError(
        "Current available protocols are 'gcs', 's3', 'local'.",
    )


def get_bucket_prefix(protocol):
    """Get protocol prefix."""
    if protocol == "gcs":
        prefix = "gs://"
    elif protocol == "s3":
        prefix = "s3://"
    elif protocol == "file":
        prefix = ""
    else:
        raise NotImplementedError(
            "Current available protocols are 'gcs', 's3', 'local'.",
        )
    return prefix


def get_simplecache_file(filepath):
    file = fsspec.open_local(
        f"simplecache::{filepath}",  # assume filepath has s3://
        s3={"anon": True},
        filecache={"cache_storage": "."},
    )
    return file


@check_software_availability(software="xradar", conda_package="xradar")
def open_datatree(filepath, network, **kwargs):
    """Open a file into an xarray DataTree object using xradar."""
    if filepath.startswith("s3"):
        filepath = get_simplecache_file(filepath)
    open_datatree = get_xradar_datatree_reader(network)
    dt = open_datatree(filepath, **kwargs)
    return dt


@check_software_availability(software="xradar", conda_package="xradar")
def open_dataset(filepath, network, group, **kwargs):
    """Open a file into an xarray Dataset object using xradar."""
    import xarray as xr

    if filepath.startswith("s3"):
        filepath = get_simplecache_file(filepath)
    engine = get_xradar_engine(network)
    ds = xr.open_dataset(filepath, group=group, engine=engine, **kwargs)
    return ds


@check_software_availability(software="pyart", conda_package="arm_pyart")
def open_pyart(filepath, network, **kwargs):
    """Open a file into a pyart object."""
    if filepath.startswith("s3"):
        filepath = get_simplecache_file(filepath)
    pyart_reader = get_pyart_reader(network)
    pyart_obj = pyart_reader(filepath, **kwargs)
    return pyart_obj

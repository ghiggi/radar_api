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
import os

import fsspec

from radar_api.checks import check_network, check_start_end_time, get_current_utc_time
from radar_api.utils.list import flatten_list
from radar_api.utils.yaml import read_yaml


def get_network_config_path():
    """Get directory path with the network configuration files."""
    from radar_api import _root_path

    path = os.path.join(_root_path, "radar_api", "etc", "network")
    return path


def get_network_radars_config_path(network):
    """Get directory path with the radar configuration files of a given network."""
    from radar_api import _root_path

    path = os.path.join(_root_path, "radar_api", "etc", "radar", network)
    return path


def get_network_config_filepath(network):
    """Get filepath of the network configuration file."""
    filepath = os.path.join(get_network_config_path(), f"{network}.yaml")
    return filepath


def get_radar_config_filepath(network, radar):
    """Get filepath of the radar configuration file."""
    filepath = os.path.join(get_network_radars_config_path(network), f"{radar}.yaml")
    return filepath


def available_networks():
    """Get list of available networks."""
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
    """Get list of available radars."""
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
    """Get network information."""
    network_config_path = get_network_config_filepath(network)
    info_dict = read_yaml(network_config_path)
    return info_dict


def get_radar_info(network, radar):
    """Get radar information."""
    network_config_path = get_radar_config_filepath(network, radar)
    info_dict = read_yaml(network_config_path)
    return info_dict


def get_radar_time_coverage(network, radar):
    """Get first and last timestep with radar data."""
    info_dict = get_radar_info(network=network, radar=radar)
    if "start_time" not in info_dict or "end_time" not in info_dict:
        raise ValueError(f"Time coverage information for {network} radar '{radar}' is unavailable.")
    start_time = info_dict["start_time"]
    end_time = info_dict["end_time"]
    start_time = datetime.datetime.fromisoformat(start_time)
    end_time = get_current_utc_time() if end_time == "" else datetime.datetime.fromisoformat(end_time)
    return start_time, end_time


def get_radar_start_time(network, radar):
    """Get first timestep with radar data."""
    time_coverage = get_radar_time_coverage(network, radar)
    if time_coverage is not None:
        return time_coverage[0]
    return None


def get_radar_end_time(network, radar):
    """Get last timestep with radar data."""
    time_coverage = get_radar_time_coverage(network, radar)
    if time_coverage is not None:
        return time_coverage[1]
    return None


def get_radar_location(network, radar):
    """Get radar location."""
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
    """Get radar filenames patterns."""
    return get_network_info(network)["filename_patterns"]


def get_directory_pattern(protocol, network):
    """Get directory pattern."""
    if protocol in ["s3", "gcs"]:
        directory_pattern = get_network_info(network)["cloud_directory_pattern"]
    else:
        directory_pattern = get_network_info(network)["local_directory_pattern"]
    return directory_pattern


def get_filesystem(protocol, fs_args=None):
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
    fs_args = {} if fs_args is None else fs_args
    if protocol == "s3":
        # Set defaults
        # - Use the anonymous credentials to access public data
        _ = fs_args.setdefault("anon", True)  # TODO: or if is empty
        fs = fsspec.filesystem("s3", **fs_args)
        return fs
    # if protocol == "gcs":
    #     # Set defaults
    #     # - Use the anonymous credentials to access public data
    #     _ = fs_args.setdefault("token", "anon")  # TODO: or if is empty
    #     fs = fsspec.filesystem("gcs", **fs_args)
    #     return fs
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
    elif protocol in ("file", "local"):
        prefix = ""
    else:
        raise NotImplementedError(
            "Current available protocols are 'gcs', 's3', 'local'.",
        )
    return prefix

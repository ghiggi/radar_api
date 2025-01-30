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
"""This module provide tools to extraction information from the granules' filenames."""
import datetime
import os
import pathlib
import sys

import numpy as np

PROTOCOLS = ["s3", "local", "file"]  # "gcs"
BUCKET_PROTOCOLS = ["s3"]  # "gcs"


def get_current_utc_time():
    """Return current UTC time."""
    if sys.version_info >= (3, 11):
        return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    return datetime.datetime.utcnow()


def check_protocol(protocol):
    """Check protocol validity."""
    if protocol is not None:
        if not isinstance(protocol, str):
            raise TypeError("`protocol` must be a string.")
        if protocol not in PROTOCOLS:
            raise ValueError(f"Valid `protocol` are {PROTOCOLS}.")
        if protocol == "local":
            protocol = "file"  # for fsspec LocalFS compatibility
    return protocol


def check_download_protocol(protocol):
    """Check protocol validity for download."""
    if protocol not in BUCKET_PROTOCOLS:
        raise ValueError("Please specify either 'gcs' or 's3' protocol for download.")


def check_base_dir(base_dir):
    """Check base_dir validity."""
    if base_dir is not None:
        if not isinstance(base_dir, (str, pathlib.Path)):
            raise TypeError("`base_dir` must be a string or a Pathlib object.")
        # Ensure is a string
        base_dir = str(base_dir)  # deal with PathLib path
        # Check base_dir does not end with /
        if base_dir[-1] == os.path.sep:
            base_dir = base_dir[0:-1]
        # Check is a directory
        if not os.path.exists(base_dir):
            raise OSError(f"`base_dir` {base_dir} does not exist.")
        if not os.path.isdir(base_dir):
            raise OSError(f"`base_dir` {base_dir} is not a directory.")
    return base_dir


def check_radar(radar, network):
    """Check radar name validity."""
    from radar_api.io import available_radars

    if not isinstance(radar, str):
        raise TypeError("Specify 'radar' as a string.")
    check_network(network)
    valid_radars = available_radars()
    if radar not in valid_radars:
        raise ValueError(f"Invalid {network} radar {radar}. Available radars: {valid_radars}")
    return radar


def check_network(network):
    """Check radar network validity."""
    from radar_api.io import available_networks

    if not isinstance(network, str):
        raise TypeError("Specify 'network' as a string.")

    valid_networks = available_networks()
    if network not in valid_networks:
        raise ValueError(f"Invalid network {network}. Available networks: {valid_networks}")
    return network


def check_time(time):
    """Check time validity.

    It returns a :py:class:`datetime.datetime` object to seconds precision.

    Parameters
    ----------
    time : datetime.datetime, datetime.date, numpy.datetime64 or str
        Time object.
        Accepted types: ``datetime.datetime``, ``datetime.date``, ``numpy.datetime64`` or ``str``.
        If string type, it expects the isoformat ``YYYY-MM-DD hh:mm:ss``.

    Returns
    -------
    time: datetime.datetime

    """
    if not isinstance(time, (datetime.datetime, datetime.date, np.datetime64, np.ndarray, str)):
        raise TypeError(
            "Specify time with datetime.datetime objects or a string of format 'YYYY-MM-DD hh:mm:ss'.",
        )

    # If numpy array with datetime64 (and size=1)
    if isinstance(time, np.ndarray):
        if np.issubdtype(time.dtype, np.datetime64):
            if time.size == 1:
                time = time[0].astype("datetime64[s]").tolist()
            else:
                raise ValueError("Expecting a single timestep!")
        else:
            raise ValueError("The numpy array does not have a numpy.datetime64 dtype!")

    # If np.datetime64, convert to datetime.datetime
    if isinstance(time, np.datetime64):
        time = time.astype("datetime64[s]").tolist()
    # If datetime.date, convert to datetime.datetime
    if not isinstance(time, (datetime.datetime, str)):
        time = datetime.datetime(time.year, time.month, time.day, 0, 0, 0)
    if isinstance(time, str):
        try:
            time = datetime.datetime.fromisoformat(time)
        except ValueError:
            raise ValueError("The time string must have format 'YYYY-MM-DD hh:mm:ss'")
    # If datetime object carries timezone that is not UTC, raise error
    if time.tzinfo is not None:
        if str(time.tzinfo) != "UTC":
            raise ValueError("The datetime object must be in UTC timezone if timezone is given.")
        # If UTC, strip timezone information
        time = time.replace(tzinfo=None)
    return time


def check_date(date):
    """Ensure the returned object is a :py:class:`datetime.date` object."""
    date = check_time(date).date()
    return date


def check_start_end_time(start_time, end_time):
    """Check start_time and end_time validity."""
    # Format input
    start_time = check_time(start_time)
    end_time = check_time(end_time)
    # Check start_time and end_time are chronological
    if start_time > end_time:
        raise ValueError("Provide start_time occurring before of end_time")
    # Check start_time is in the past
    if start_time > get_current_utc_time():
        raise ValueError("Provide a start_time occurring in the past.")

    # end_time must not be checked if wanting to search on latest file available !
    # if end_time > get_current_utc_time():
    #     raise ValueError("Provide a end_time occurring in the past.")
    return (start_time, end_time)

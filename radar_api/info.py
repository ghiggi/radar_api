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
"""This module provide tools to extraction information from the granules' filenames."""

import os
import re
from collections import defaultdict

import numpy as np
from trollsift import Parser

from radar_api.io import get_network_filename_patterns

# TODO: Create a class all such methods that depend on the filename_patterns and network

####---------------------------------------------------------------------------.
##########################
#### Filename parsers ####
##########################


def parse_filename(filename, network):
    filename_patterns = get_network_filename_patterns(network)
    pattern_identified = False
    for pattern in filename_patterns:
        try:
            p = Parser(pattern)
            info_dict = p.parse(filename)
            pattern_identified = True
        except Exception:
            pass
        if pattern_identified:
            break
    if not pattern_identified:
        # print(f"Report the bug for filename '{filename}'.")
        info_dict = {}
    return info_dict


def _get_info_from_filename(filename, network):
    """Retrieve file information dictionary from filename."""
    try:
        info_dict = parse_filename(filename, network=network)
    except Exception:
        raise ValueError(f"Impossible to infer file information from '{filename}'")
    # Set default volume_identifier if missing
    if "volume_identifier" not in info_dict:
        info_dict["volume_identifier"] = ""
    return info_dict


def get_info_from_filepath(filepath, network):
    """Retrieve file information dictionary from filepath."""
    if not isinstance(filepath, str):
        raise TypeError("'filepath' must be a string.")
    filename = os.path.basename(filepath)
    return _get_info_from_filename(filename, network=network)


def get_key_from_filepath(filepath, key, network):
    """Extract specific key information from a list of filepaths."""
    return get_info_from_filepath(filepath, network=network)[key]


def get_key_from_filepaths(filepaths, key, network):
    """Extract specific key information from a list of filepaths."""
    if isinstance(filepaths, str):
        filepaths = [filepaths]
    return [get_key_from_filepath(filepath, key=key, network=network) for filepath in filepaths]


####--------------------------------------------------------------------------.
#########################################
#### Product and version information ####
#########################################


def get_version_from_filepath(filepath, network, integer=True):
    """Infer file ``version`` from filenames."""
    version = get_key_from_filepath(filepath, key="version", network=network)
    if integer:
        version = int(re.findall("\\d+", version)[0])
    return version


def get_version_from_filepaths(filepaths, network, integer=True):
    """Infer files ``version`` from filenames."""
    if isinstance(filepaths, str):
        filepaths = [filepaths]
    return [get_version_from_filepath(filepath, integer=integer, network=network) for filepath in filepaths]


def get_start_time_from_filepaths(filepaths, network):
    """Infer files ``start_time`` from filenames."""
    return get_key_from_filepaths(filepaths, key="start_time", network=network)


def get_end_time_from_filepaths(filepaths, network):
    """Infer files ``end_time`` from filenames."""
    return get_key_from_filepaths(filepaths, key="end_time", network=network)


def get_start_end_time_from_filepaths(filepaths, network):
    """Infer files ``start_time`` and ``end_time`` from filenames."""
    list_start_time = get_key_from_filepaths(filepaths, key="start_time", network=network)
    list_end_time = get_key_from_filepaths(filepaths, key="end_time", network=network)
    return np.array(list_start_time), np.array(list_end_time)


####--------------------------------------------------------------------------.
#######################
#### Group utility ####
#######################


FILE_KEYS = [
    "radar_acronym",
    "volume_identifier",
    "start_time",
    "end_time",
    "version",
    "extension",
]

TIME_KEYS = [
    "year",
    "month",
    "month_name",
    "quarter",
    "season",
    "day",
    "doy",
    "dow",
    "hour",
    "minute",
    "second",
]


def check_groups(groups):
    """Check groups validity."""
    if not isinstance(groups, (str, list)):
        raise TypeError("'groups' must be a list (or a string if a single group is specified.")
    if isinstance(groups, str):
        groups = [groups]
    groups = np.array(groups)
    valid_keys = FILE_KEYS + TIME_KEYS
    invalid_keys = groups[np.isin(groups, valid_keys, invert=True)]
    if len(invalid_keys) > 0:
        raise ValueError(f"The following group keys are invalid: {invalid_keys}. Valid values are {valid_keys}.")
    return groups.tolist()


def get_season(time):
    """Get season from `datetime.datetime` or `datetime.date` object."""
    month = time.month
    if month in [12, 1, 2]:
        return "DJF"  # Winter (December, January, February)
    if month in [3, 4, 5]:
        return "MAM"  # Spring (March, April, May)
    if month in [6, 7, 8]:
        return "JJA"  # Summer (June, July, August)
    return "SON"  # Autumn (September, October, November)


def get_time_component(time, component):
    """Get time component from `datetime.datetime` object."""
    func_dict = {
        "year": lambda time: time.year,
        "month": lambda time: time.month,
        "day": lambda time: time.day,
        "doy": lambda time: time.timetuple().tm_yday,  # Day of year
        "dow": lambda time: time.weekday(),  # Day of week (0=Monday, 6=Sunday)
        "hour": lambda time: time.hour,
        "minute": lambda time: time.minute,
        "second": lambda time: time.second,
        # Additional
        "month_name": lambda time: time.strftime("%B"),  # Full month name
        "quarter": lambda time: (time.month - 1) // 3 + 1,  # Quarter (1-4)
        "season": lambda time: get_season(time),  # Season (DJF, MAM, JJA, SON)
    }
    return str(func_dict[component](time))


def _get_groups_value(groups, filepath, network):
    """Return the value associated to the groups keys.

    If multiple keys are specified, the value returned is a string of format: ``<group_value_1>/<group_value_2>/...``

    If a single key is specified and is ``start_time`` or ``end_time``, the function
    returns a :py:class:`datetime.datetime` object.
    """
    single_key = len(groups) == 1
    info_dict = get_info_from_filepath(filepath, network=network)
    start_time = info_dict["start_time"]
    list_key_values = []
    for key in groups:
        if key in TIME_KEYS:
            list_key_values.append(get_time_component(start_time, component=key))
        else:
            value = info_dict.get(key, f"{key}=None")
            list_key_values.append(value if single_key else str(value))
    if single_key:
        return list_key_values[0]
    return "/".join(list_key_values)


def group_filepaths(filepaths, network, groups=None):
    """
    Group filepaths in a dictionary if groups are specified.

    Parameters
    ----------
    filepaths : list
        List of filepaths.
    groups: list or str
        The group keys by which to group the filepaths.
        Valid group keys are
        ``start_time``, ``end_time``, ``version``, ``volume_identifier``, ``radar_acronym``, ``extension``,
        ``year``, ``month``, ``day``,  ``doy``, ``dow``, ``hour``, ``minute``, ``second``,
        ``month_name``, ``quarter``, ``season``.
        The time components are extracted from ``start_time`` !
        If groups is ``None`` returns the input filepaths list.
        The default is ``None``.

    Returns
    -------
    dict or list
        Either a dictionary of format ``{<group_value>: <list_filepaths>}``.
        or the original input filepaths (if ``groups=None``)

    """
    if groups is None:
        return filepaths
    groups = check_groups(groups)
    filepaths_dict = defaultdict(list)
    _ = [
        filepaths_dict[_get_groups_value(groups, filepath, network=network)].append(filepath) for filepath in filepaths
    ]
    return dict(filepaths_dict)

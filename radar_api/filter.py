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
"""Filtering functions."""
import datetime

from radar_api.info import get_info_from_filepath


def is_file_within_time(start_time, end_time, file_start_time, file_end_time):
    """Check if a file is within start_time and end_time."""
    # - Case 1
    #     s               e
    #     |               |
    #   ---------> (-------->)
    is_case1 = file_start_time <= start_time and file_end_time > start_time
    # - Case 2
    #     s               e
    #     |               |
    #          --------
    is_case2 = file_start_time >= start_time and file_end_time < end_time
    # - Case 3
    #     s               e
    #     |               |
    #                ------------->
    is_case3 = file_start_time < end_time and file_end_time > end_time
    # - Check if one of the conditions occurs
    return is_case1 or is_case2 or is_case3


def filter_file(fpath, network, start_time, end_time):
    """Utility function to select a file is matching the specified time periods."""
    # Filter by start_time
    if start_time is not None and end_time is not None:
        # Retrieve info
        info_dict = get_info_from_filepath(fpath, network=network)
        if "start_time" not in info_dict:
            return None
        # Retrieve file start time and end time
        file_start_time = info_dict.get("start_time")
        if info_dict.get("end_time", None) is None:
            file_end_time = file_start_time + datetime.timedelta(
                minutes=15,
            )  # TODO: maybe based on file_time_coverage setting?
        else:
            file_end_time = info_dict.get("end_time")

        if not is_file_within_time(start_time, end_time, file_start_time, file_end_time):
            return None
    return fpath


def filter_files(
    fpaths,
    network,
    start_time=None,
    end_time=None,
):
    """Utility function to select filepaths between time periods."""
    if isinstance(fpaths, str):
        fpaths = [fpaths]
    fpaths = [
        filter_file(
            fpath,
            network=network,
            start_time=start_time,
            end_time=end_time,
        )
        for fpath in fpaths
    ]
    fpaths = [fpath for fpath in fpaths if fpath is not None]
    return fpaths

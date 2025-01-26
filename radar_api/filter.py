#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 22:38:09 2025

@author: ghiggi
"""
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
            file_end_time = file_start_time + datetime.timedelta(minutes=15) # TODO: maybe based on file_time_coverage setting? 
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
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
"""Define download functions."""

import concurrent.futures
import datetime
import os
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
from tqdm import tqdm
from trollsift import Parser

from radar_api.checks import (
    check_base_dir,
    check_download_protocol,
    check_network,
    check_radar,
    check_start_end_time,
)
from radar_api.configs import get_base_dir
from radar_api.info import get_info_from_filepath
from radar_api.io import get_directory_pattern, get_filesystem
from radar_api.search import find_files
from radar_api.utils.timing import print_elapsed_time

####--------------------------------------------------------------------------.


def create_local_directories(fpaths, exist_ok=True):
    """Create recursively local directories for the provided filepaths."""
    _ = [os.makedirs(os.path.dirname(fpath), exist_ok=exist_ok) for fpath in fpaths]


def remove_corrupted_files(local_fpaths, bucket_fpaths, fs, return_corrupted_fpaths=True):
    """
    Check and remove files from local disk which are corrupted.

    Corruption is evaluated by comparing the size of data on local storage against
    size of data located in the cloud bucket.

    Parameters
    ----------
    local_fpaths : list
        List of filepaths on local storage.
    bucket_fpaths : list
        List of filepaths on cloud bucket.
    fs : ffspec.FileSystem
        ffspec filesystem instance.
        It must be cohrenet with the cloud bucket address of bucket_fpaths.
    return_corrupted_fpaths : bool, optional
        If True, it returns the list of corrupted files.
        If False, it returns the list of valid files.
        The default is True.

    Returns
    -------
    (list_<valid/corrupted>_local_filepaths, list_<valid/corrupted>_bucket_filepaths)

    """
    l_corrupted_local = []
    l_corrupted_bucket = []
    l_valid_local = []
    l_valid_bucket = []
    for local_fpath, bucket_fpath in zip(local_fpaths, bucket_fpaths, strict=False):
        local_exists = os.path.isfile(local_fpath)
        if local_exists:
            bucket_size = fs.info(bucket_fpath)["size"]
            local_size = os.path.getsize(local_fpath)
            if bucket_size != local_size:
                os.remove(local_fpath)
                l_corrupted_local.append(local_fpath)
                l_corrupted_bucket.append(bucket_fpath)
            else:
                l_valid_local.append(local_fpath)
                l_valid_bucket.append(bucket_fpath)
    if return_corrupted_fpaths:
        return l_corrupted_local, l_corrupted_bucket
    return l_valid_local, l_valid_bucket


def _select_missing_fpaths(local_fpaths, bucket_fpaths):
    """Return local and bucket filepaths of files not present on the local storage."""
    # Keep only non-existing local files
    idx_not_exist = [not os.path.exists(filepath) for filepath in local_fpaths]
    local_fpaths = np.array(local_fpaths)[idx_not_exist].tolist()
    bucket_fpaths = np.array(bucket_fpaths)[idx_not_exist].tolist()
    return local_fpaths, bucket_fpaths


def _remove_bucket_address(fpath):
    """Remove the bucket acronym (i.e. s3://, gcs://) from the file path."""
    fel = fpath.split("/")[3:]
    fpath = os.path.join(*fel)
    return fpath


def define_local_filepath(filename, network, radar, base_dir):
    """Define filepath where to save file locally on disk."""
    # Get directory pattern
    directory_pattern = get_directory_pattern(protocol="local", network=network)
    info_dict = get_info_from_filepath(filename, network=network)
    time = info_dict["start_time"]
    # Define local directory path
    parser = Parser(directory_pattern)
    path = parser.compose({"time": time, "radar": radar, "base_dir": base_dir})
    filepath = os.path.join(path, filename)
    return filepath


def _get_local_from_bucket_fpaths(base_dir, network, radar, bucket_fpaths):
    """Convert cloud bucket filepaths to local storage filepaths."""
    fpaths = [
        define_local_filepath(filename=os.path.basename(fpath), network=network, radar=radar, base_dir=base_dir)
        for fpath in bucket_fpaths
    ]
    return fpaths


def _fs_get_parallel(bucket_fpaths, local_fpaths, fs, n_threads=10, progress_bar=True):
    """
    Run fs.get() asynchronously in parallel using multithreading.

    Parameters
    ----------
    bucket_fpaths : list
        List of bucket filepaths to download.
    local_fpath : list
        List of filepaths where to save data on local storage.
    n_threads : int, optional
        Number of files to be downloaded concurrently.
        The default is 10. The max value is set automatically to 50.

    Returns
    -------
    List of cloud bucket filepaths which were not downloaded.
    """
    # Check n_threads
    n_threads = max(n_threads, 1)
    n_threads = min(n_threads, 50)

    ##------------------------------------------------------------------------.
    # Initialize progress bar
    if progress_bar:
        n_files = len(local_fpaths)
        pbar = tqdm(total=n_files)
    with ThreadPoolExecutor(max_workers=n_threads) as executor:
        dict_futures = {
            executor.submit(fs.get, bucket_path, local_fpath): bucket_path
            for bucket_path, local_fpath in zip(bucket_fpaths, local_fpaths, strict=False)
        }
        # List files that didn't work
        l_file_error = []
        for future in concurrent.futures.as_completed(dict_futures.keys()):
            # Update the progress bar
            if progress_bar:
                pbar.update(1)
            # Collect all commands that caused problems
            if future.exception() is not None:
                l_file_error.append(dict_futures[future])
    if progress_bar:
        pbar.close()
    ##------------------------------------------------------------------------.
    # Return list of bucket fpaths raising errors
    return l_file_error


def _get_end_of_day(time):
    """Get datetime end of the day."""
    time_end_of_day = time + datetime.timedelta(days=1)
    time_end_of_day = time_end_of_day.replace(hour=0, minute=0, second=0)
    return time_end_of_day


def _get_start_of_day(time):
    """Get datetime start of the day."""
    time_start_of_day = time
    time_start_of_day = time_start_of_day.replace(hour=0, minute=0, second=0)
    return time_start_of_day


def _get_list_daily_time_blocks(start_time, end_time):
    """Return a list of (start_time, end_time) tuple of daily length."""
    # Retrieve timedelta between start_time and end_time
    dt = end_time - start_time
    # If less than a day
    if dt.days == 0:
        return [(start_time, end_time)]
    # Otherwise split into daily blocks (first and last can be shorter)
    end_of_start_time = _get_end_of_day(start_time)
    start_of_end_time = _get_start_of_day(end_time)
    # Define list of daily blocks
    l_steps = pd.date_range(end_of_start_time, start_of_end_time, freq="1D")
    l_steps = l_steps.to_pydatetime().tolist()
    l_steps.insert(0, start_time)
    l_steps.append(end_time)
    l_daily_blocks = [(l_steps[i], l_steps[i + 1]) for i in range(0, len(l_steps) - 1)]
    return l_daily_blocks


####---------------------------------------------------------------------------.
@print_elapsed_time
def download_files(
    network,
    radar,
    start_time,
    end_time,
    n_threads=20,
    force_download=False,
    check_data_integrity=True,
    progress_bar=True,
    verbose=True,
    base_dir=None,
    protocol="s3",
    fs_args={},
):
    """
    Download files from a cloud bucket storage.

    Parameters
    ----------
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
    base_dir : str, optional
        The path to the directory where to store GOES data.
        If None, it use the one specified  in the GOES-API config file.
        The default is None.
    fs_args : dict, optional
        Dictionary specifying optional settings to initiate the fsspec.filesystem.
        The default is an empty dictionary. Anonymous connection is set by default.
    n_threads: int
        Number of files to be downloaded concurrently.
        The default is 20. The max value is set automatically to 50.
    force_download: bool
        If True, it downloads and overwrites the files already existing on local storage.
        If False, it does not downloads files already existing on local storage.
        The default is False.
    check_data_integrity: bool
        If True, it checks that the downloaded files are not corrupted.
        Corruption is assessed by comparing file size between local and cloud bucket storage.
        The default is True.
    progress_bar: bool
        If True, it displays a progress bar showing the download status.
        The default is True.
    verbose : bool, optional
        If True, it print some information concerning the download process.
        The default is False.

    """
    # -------------------------------------------------------------------------.
    # Get default directory
    base_dir = get_base_dir(base_dir)
    # Checks
    check_download_protocol(protocol)
    base_dir = check_base_dir(base_dir)
    network = check_network(network)
    radar = check_radar(radar=radar, network=network)
    start_time, end_time = check_start_end_time(start_time, end_time)

    # Initialize timing
    t_i = time.time()

    # -------------------------------------------------------------------------.
    # Get filesystem
    fs = get_filesystem(protocol=protocol, fs_args=fs_args)

    # Define list of daily time blocks (start_time, end_time)
    time_blocks = _get_list_daily_time_blocks(start_time, end_time)

    if verbose:
        print("-------------------------------------------------------------------- ")
        print(f"Starting downloading {network.upper()} {radar} data between {start_time} and {end_time}.")

    # Loop over daily time blocks (to search for data)
    list_all_local_fpaths = []
    list_all_bucket_fpaths = []
    n_downloaded_files = 0
    n_existing_files = 0
    n_total_files = 0
    for start_time, end_time in time_blocks:
        # Retrieve bucket fpaths
        bucket_fpaths = find_files(
            protocol=protocol,
            fs_args=fs_args,
            radar=radar,
            network=network,
            start_time=start_time,
            end_time=end_time,
            base_dir=None,
            verbose=False,
        )
        # Check there are files to retrieve
        n_files = len(bucket_fpaths)
        n_total_files += n_files
        if n_files == 0:
            continue

        # Define local destination fpaths
        local_fpaths = _get_local_from_bucket_fpaths(
            base_dir=base_dir,
            network=network,
            radar=radar,
            bucket_fpaths=bucket_fpaths,
        )

        # Record the local and bucket fpath queried
        list_all_local_fpaths = list_all_local_fpaths + local_fpaths
        list_all_bucket_fpaths = list_all_bucket_fpaths + bucket_fpaths

        # Optionally exclude files that already exist on disk
        if not force_download:
            local_fpaths, bucket_fpaths = _select_missing_fpaths(
                local_fpaths=local_fpaths,
                bucket_fpaths=bucket_fpaths,
            )
            # Update count of existing files on disk
            n_existing_files += n_files - len(bucket_fpaths)

        # Check there are still files to retrieve
        n_files = len(local_fpaths)
        n_downloaded_files += n_files
        if n_files == 0:
            continue

        # Create local directories
        create_local_directories(local_fpaths)

        # Print # files to download
        if verbose:
            print(f" - Downloading {n_files} files from {start_time} to {end_time}")

        # Download data asynchronously with multithreading
        l_bucket_errors = _fs_get_parallel(
            bucket_fpaths=bucket_fpaths,
            local_fpaths=local_fpaths,
            fs=fs,
            n_threads=n_threads,
            progress_bar=progress_bar,
        )
        # Report errors if occurred
        if verbose:
            n_errors = len(l_bucket_errors)
            if n_errors > 0:
                print(f" - Unable to download the following files: {l_bucket_errors}")

    # Report the total number of file downloaded
    if verbose:
        t_f = time.time()
        t_elapsed = round(t_f - t_i)
        if not force_download and n_existing_files > 0:
            print(
                f" - {n_existing_files}/{n_total_files} files were already present on disk !",
            )
        if n_downloaded_files > 0:
            print(
                f" - {n_downloaded_files}/{n_total_files} files have been downloaded in {t_elapsed} seconds !",
            )

        print("-------------------------------------------------------------------- ")

    # Check for data corruption
    if check_data_integrity:
        if verbose:
            print("Checking data integrity:")
        list_all_local_fpaths, _ = remove_corrupted_files(
            list_all_local_fpaths,
            list_all_bucket_fpaths,
            fs=fs,
            return_corrupted_fpaths=False,
        )
        if verbose:
            n_corrupted = len(list_all_bucket_fpaths) - len(list_all_local_fpaths)
            print(f" - {n_corrupted} corrupted files were identified and removed.")
            print(
                "--------------------------------------------------------------------",
            )

    # Return list of local fpaths
    return sorted(list_all_local_fpaths)


####---------------------------------------------------------------------------.

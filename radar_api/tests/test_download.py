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

# -----------------------------------------------------------------------------.
"""This module test the files download routines."""
import datetime
import os

from radar_api.download import (
    define_local_filepath,
    download_files,
    get_end_of_day,
    get_list_daily_time_blocks,
    get_start_of_day,
)


class TestDayBoundaries:
    def test_get_start_of_day(self):
        """Test _get_start_of_day returns datetime with hour=minute=second=0."""
        time = datetime.datetime(2023, 7, 10, 15, 45, 30)
        start_of_day = get_start_of_day(time)
        assert start_of_day == datetime.datetime(2023, 7, 10, 0, 0, 0)

    def test_get_end_of_day(self):
        """Test _get_end_of_day returns the next midnight."""
        time = datetime.datetime(2023, 7, 10, 15, 45, 30)
        end_of_day = get_end_of_day(time)
        assert end_of_day == datetime.datetime(2023, 7, 11, 0, 0, 0)

        time = datetime.datetime(2023, 7, 12, 0, 0, 0)
        end_of_day = get_end_of_day(time)
        assert end_of_day == datetime.datetime(2023, 7, 13, 0, 0, 0)


##############################
# Tests for get_list_daily_time_blocks()
##############################
class TestGetListDailyTimeBlocks:
    def test_same_day(self):
        """Test single-day interval returns a single (start, end) tuple."""
        start_time = datetime.datetime(2023, 7, 10, 10, 0, 0)
        end_time = datetime.datetime(2023, 7, 10, 18, 0, 0)
        result = get_list_daily_time_blocks(start_time, end_time)
        assert len(result) == 1
        assert result[0] == (start_time, end_time)

    def test_less_than_one_day_spanning_midnight(self):
        """Test interval <24h spanning midnight is returned as a single block."""
        # Even though it crosses midnight, total duration < 1 day => single tuple
        start_time = datetime.datetime(2023, 7, 10, 20, 0, 0)
        end_time = datetime.datetime(2023, 7, 11, 10, 0, 0)
        result = get_list_daily_time_blocks(start_time, end_time)
        assert len(result) == 1
        assert result[0] == (start_time, end_time)

    def test_two_full_days(self):
        """Test interval of exactly 48 hours returns two daily blocks."""
        start_time = datetime.datetime(2023, 7, 10, 0, 0, 0)
        end_time = datetime.datetime(2023, 7, 12, 0, 0, 0)
        result = get_list_daily_time_blocks(start_time, end_time)
        # We expect blocks:
        # (7/10 00:00, 7/11 00:00),
        # (7/11 00:00, 7/12 00:00)]
        assert len(result) == 2
        assert result[0] == (
            datetime.datetime(2023, 7, 10, 0, 0, 0),
            datetime.datetime(2023, 7, 11, 0, 0, 0),
        )
        assert result[1] == (
            datetime.datetime(2023, 7, 11, 0, 0, 0),
            datetime.datetime(2023, 7, 12, 0, 0, 0),
        )

    def test_multi_day_interval(self):
        """Test multi-day interval returns a list of daily blocks."""
        start_time = datetime.datetime(2023, 7, 10, 8, 30, 0)
        end_time = datetime.datetime(2023, 7, 13, 9, 45, 0)
        # We expect blocks:
        # (7/10 08:30, 7/11 00:00),
        # (7/11 00:00, 7/12 00:00),
        # (7/12 00:00, 7/13 00:00),
        # (7/13 00:00, 7/13 09:45)
        result = get_list_daily_time_blocks(start_time, end_time)
        assert len(result) == 4
        assert result[0] == (
            datetime.datetime(2023, 7, 10, 8, 30),
            datetime.datetime(2023, 7, 11, 0, 0),
        )
        assert result[1] == (
            datetime.datetime(2023, 7, 11, 0, 0),
            datetime.datetime(2023, 7, 12, 0, 0),
        )
        assert result[2] == (
            datetime.datetime(2023, 7, 12, 0, 0),
            datetime.datetime(2023, 7, 13, 0, 0),
        )
        assert result[3] == (
            datetime.datetime(2023, 7, 13, 0, 0),
            datetime.datetime(2023, 7, 13, 9, 45),
        )


def test_define_local_filepath(tmp_path):
    """Test the define_local_filepath function."""
    filename = "KTLX19910605_162126.gz"
    network = "NEXRAD"
    radar = "KTLX"
    base_dir = os.path.join(tmp_path, "RADAR")
    os.makedirs(base_dir, exist_ok=True)
    res = define_local_filepath(filename=filename, network=network, radar=radar, base_dir=base_dir)
    assert res == os.path.join(base_dir, network, "1991", "06", "05", "16", radar, filename)


def test_find_files_on_cloud_bucket(tmp_path):
    """Test the find_files function on the s3 cloud bucket."""
    base_dir = tmp_path
    radar = "KTLX"
    network = "NEXRAD"
    start_time = "1991-06-05T16:20:00"
    end_time = "1991-06-05T16:22:00"  # download only the first file available ...
    filepaths = download_files(
        network=network,
        radar=radar,
        start_time=start_time,
        end_time=end_time,
        verbose=True,
        n_threads=4,
        base_dir=base_dir,
        force_download=False,
        check_data_integrity=True,
        progress_bar=True,
    )
    assert isinstance(filepaths, list)
    assert len(filepaths) == 1
    assert filepaths[0].endswith("KTLX19910605_162126.gz")

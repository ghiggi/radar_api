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
"""This module test the files search routines."""
import os
import shutil

import pandas as pd
import pytest

import radar_api
from radar_api.search import (
    find_files,
    get_directories_paths,
    get_list_timesteps,
    get_pattern_shortest_time_component,
)


class TestIdentifyLastTimeComponent:
    def test_minute_component(self):
        """Test get_pattern_shortest_time_component returns 'min' for pattern with {time:%M}."""
        pattern = "some_path/{time:%Y}/{time:%m}/{time:%d}/{time:%H}/{time:%M}"
        freq = get_pattern_shortest_time_component(pattern)
        assert freq == "min"

    def test_hour_component(self):
        """Test get_pattern_shortest_time_component returns 'h' for pattern with {time:%H}."""
        pattern = "some_path/{time:%Y}/{time:%m}/{time:%d}/{time:%H}"
        freq = get_pattern_shortest_time_component(pattern)
        assert freq == "h"

    def test_day_component(self):
        """Test get_pattern_shortest_time_component returns 'D' for pattern with {time:%d}."""
        pattern = "some_path/{time:%Y}/{time:%m}/{time:%d}"
        freq = get_pattern_shortest_time_component(pattern)
        assert freq == "D"

    def test_month_component(self):
        """Test get_pattern_shortest_time_component returns 'MS' for pattern with {time:%m}."""
        pattern = "some_path/{time:%Y}/{time:%m}"
        freq = get_pattern_shortest_time_component(pattern)
        assert freq == "MS"

    def test_year_component(self):
        """Test get_pattern_shortest_time_component returns 'Y' for pattern with {time:%Y}."""
        pattern = "some_path/{time:%Y}"
        freq = get_pattern_shortest_time_component(pattern)
        assert freq == "Y"

    def test_not_implemented(self):
        """Test get_pattern_shortest_time_component raises NotImplementedError if unknown format."""
        pattern = "some_path/{time:%S}"  # seconds not handled by the function
        with pytest.raises(NotImplementedError):
            get_pattern_shortest_time_component(pattern)


class TestGetListTimesteps:
    @pytest.mark.parametrize(
        ("freq", "start_str", "end_str", "expected_dates"),
        [
            # freq='D' => shift start back by 1 day, then floor both
            (
                "D",
                "2023-07-01 12:00:00",
                "2023-07-02 01:00:00",
                [pd.Timestamp("2023-06-30"), pd.Timestamp("2023-07-01"), pd.Timestamp("2023-07-02")],
            ),
            # freq='h' => shift start back by 1 hour, then floor hours
            (
                "h",
                "2023-07-01 12:30:00",
                "2023-07-01 13:45:00",
                [
                    pd.Timestamp("2023-07-01 11:00:00"),
                    pd.Timestamp("2023-07-01 12:00:00"),
                    pd.Timestamp("2023-07-01 13:00:00"),
                ],
            ),
            # freq='min' => shift start back by 1 minute, floor minutes
            (
                "min",
                "2023-07-01 12:30:30",
                "2023-07-01 12:32:10",
                [
                    pd.Timestamp("2023-07-01 12:29:00"),
                    pd.Timestamp("2023-07-01 12:30:00"),
                    pd.Timestamp("2023-07-01 12:31:00"),
                    pd.Timestamp("2023-07-01 12:32:00"),
                ],
            ),
        ],
    )
    def test_frequencies(self, freq, start_str, end_str, expected_dates):
        """Test get_list_timesteps with day/hour/minute frequencies."""
        times = get_list_timesteps(start_str, end_str, freq)
        assert list(times) == expected_dates

    def test_freq_ms(self):
        """Test get_list_timesteps with freq='MS' (monthly start)."""
        start_time = "2023-01-15"
        end_time = "2023-02-10"
        times = get_list_timesteps(start_time, end_time, freq="MS")
        # freq='MS' means we shift start_time's month back by 1,
        # and then produce monthly steps from 2022-12-01 to 2023-02-01
        assert list(times) == [
            pd.Timestamp("2022-12-01"),
            pd.Timestamp("2023-01-01"),
            pd.Timestamp("2023-02-01"),
        ]

        start_time = "2023-02-15"
        end_time = "2023-03-10"
        times = get_list_timesteps(start_time, end_time, freq="MS")
        assert list(times) == [
            pd.Timestamp("2023-01-01"),
            pd.Timestamp("2023-02-01"),
            pd.Timestamp("2023-03-01"),
        ]

    def test_freq_y(self):
        """Test get_list_timesteps with freq='Y' (yearly)."""
        start_time = "2024-06-10"
        end_time = "2026-02-01"
        times = get_list_timesteps(start_time, end_time, freq="Y")
        # freq='Y' (YE-DEC) means shift start year back by 1 => 2023,
        assert list(times) == [
            pd.Timestamp("2023-12-31"),
            pd.Timestamp("2024-12-31"),
            pd.Timestamp("2025-12-31"),
            pd.Timestamp("2026-12-31"),
        ]

    def test_unhandled_freq(self):
        """Test get_list_timesteps raises NotImplementedError for unknown freq."""
        with pytest.raises(NotImplementedError):
            get_list_timesteps("2023-01-01", "2023-02-01", freq="S")  # seconds not supported


class TestGetDirectoriesPaths:
    def test_directories_s3_day(self):
        """Test get_directories_paths for s3 daily pattern with partial day range."""
        start_time = "2023-07-01T12:00:00"
        end_time = "2023-07-02T01:00:00"
        network = "NEXRAD"
        radar = "KFSD"
        protocol = "s3"
        base_dir = None

        # directory_pattern for protocol="s3" is 's3://noaa-nexrad-level2/{time:%Y}/{time:%m}/{time:%d}/{radar:s}'
        # => The last time component is {time:%d} => freq='D'
        # => We'll generate times for 2023-06-30, 2023-07-01, 2023-07-02

        paths = get_directories_paths(
            start_time=start_time,
            end_time=end_time,
            network=network,
            radar=radar,
            protocol=protocol,
            base_dir=base_dir,
        )
        expected = [
            # Because the function does start_time - 1 day, then floors to day ...
            "s3://noaa-nexrad-level2/2023/06/30/KFSD",
            "s3://noaa-nexrad-level2/2023/07/01/KFSD",
            "s3://noaa-nexrad-level2/2023/07/02/KFSD",
        ]
        assert paths == expected


def test_find_files_on_cloud_bucket():
    """Test the find_files function on the s3 cloud bucket."""
    radar = "KABR"
    network = "NEXRAD"
    start_time = "2023-07-01T12:00:00"
    end_time = "2023-07-01T13:00:00"
    filepaths = find_files(
        network=network,
        radar=radar,
        start_time=start_time,
        end_time=end_time,
        protocol="s3",
        verbose=True,
    )
    assert isinstance(filepaths, list)
    assert len(filepaths) == 12


def test_find_files_on_local_disk(tmp_path):
    """Test the find_files function on local disk."""
    # Copy sample file to temporary local directory
    filepath = os.path.join(radar_api._root_path, "radar_api", "tests", "test_data", "KABR20230101_000142_V06")
    base_dir = os.path.join(tmp_path, "RADAR")
    dst_dir = os.path.join(base_dir, "NEXRAD", "2023", "01", "01", "00", "KABR")
    dst_fpath = os.path.join(dst_dir, os.path.basename(filepath))
    os.makedirs(dst_dir, exist_ok=True)
    shutil.copy(filepath, dst_fpath)

    # Check the file is found on the local disk
    radar = "KABR"
    network = "NEXRAD"
    start_time = "2023-01-01T00:00:00"
    end_time = "2023-01-01T01:00:00"
    filepaths = find_files(
        network=network,
        radar=radar,
        start_time=start_time,
        end_time=end_time,
        protocol="local",
        base_dir=base_dir,
        verbose=True,
    )
    assert isinstance(filepaths, list)
    assert len(filepaths) == 1
    assert filepaths[0].endswith("KABR20230101_000142_V06")


def test_find_files_invalid_arguments():
    """Test the find_files raise error if base_dir specified with cloud protocol."""
    radar = "KABR"
    network = "NEXRAD"
    start_time = "2023-07-01T12:00:00"
    end_time = "2023-07-01T13:00:00"
    with pytest.raises(ValueError):
        find_files(
            network=network,
            radar=radar,
            start_time=start_time,
            end_time=end_time,
            protocol="s3",
            base_dir="base_dir_path_with_s3_protocol",
        )

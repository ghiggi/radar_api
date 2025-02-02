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
"""This module test the I/O routines."""
import datetime
import os

import fsspec
import pytest
import s3fs

from radar_api.io import (
    available_networks,
    available_radars,
    get_bucket_prefix,
    get_directory_pattern,
    get_filesystem,
    get_network_config_filepath,
    get_network_config_path,
    get_network_filename_patterns,
    get_network_info,
    get_network_radars_config_path,
    get_radar_config_filepath,
    get_radar_end_time,
    get_radar_info,
    get_radar_location,
    get_radar_start_time,
    get_radar_time_coverage,
    is_radar_available,
)

NETWORKS = available_networks()


def test_get_network_config_path():
    """Test get_network_config_path returns the network configuration directory."""
    path = get_network_config_path()
    assert os.path.isdir(path)


def test_get_network_radars_config_path():
    """Test get_network_radars_config_path with NEXRAD."""
    path = get_network_radars_config_path("NEXRAD")
    assert os.path.isdir(path)
    assert "NEXRAD" in path


@pytest.mark.parametrize("network", NETWORKS)
def test_get_network_config_filepath(network):
    """Test get_network_config_filepath returns the correct .yaml file path."""
    filepath = get_network_config_filepath(network)
    assert os.path.isfile(filepath)
    assert filepath.endswith(f"{network}.yaml")


@pytest.mark.parametrize("network", NETWORKS)
def test_get_radar_config_filepath(network):
    """Test get_radar_config_filepath returns correct file path for a radar."""
    for radar in available_radars(network=network):
        filepath = get_radar_config_filepath(network, radar)
        assert os.path.isfile(filepath)
        assert filepath.endswith(f"{radar}.yaml")


def test_available_networks():
    """Test available_networks."""
    nets = available_networks()
    assert "NEXRAD" in nets


def test_available_radars_all_networks():
    """Test available_radars()."""
    radars = available_radars()
    assert isinstance(radars, list)


def test_available_radars_single_network():
    """Test available_radars(network)."""
    radars = available_radars("NEXRAD")
    assert isinstance(radars, list)


def test_get_network_info():
    """Test get_network_info returns the correct dict from NEXRAD.yaml."""
    info = get_network_info("NEXRAD")
    assert info["xradar_reader"] == "open_nexradlevel2_datatree"
    assert info["pyart_reader"] == "read_nexrad_archive"


def test_get_radar_info():
    """Test get_radar_info returns the radar config dictionary."""
    info = get_radar_info(network="NEXRAD", radar="KABR")
    assert info["end_time"] == ""  # WHEN RADAR IS STILL AVAILABLE


def test_get_radar_time_coverage():
    """Test get_radar_time_coverage returns start/end as datetimes."""
    start_time, end_time = get_radar_time_coverage(network="NEXRAD", radar="KABR")
    assert isinstance(start_time, datetime.datetime)
    assert isinstance(end_time, datetime.datetime)


def test_get_radar_start_time():
    """Test get_radar_start_time returns the correct datetime."""
    start_time = get_radar_start_time(network="NEXRAD", radar="KABR")
    assert isinstance(start_time, datetime.datetime)


def test_get_radar_end_time():
    """Test get_radar_end_time returns the correct datetime."""
    end_time = get_radar_end_time(network="NEXRAD", radar="KABR")
    assert isinstance(end_time, datetime.datetime)


def test_get_radar_location():
    """Test get_radar_location returns (longitude, latitude)."""
    lon, lat = get_radar_location(network="NEXRAD", radar="KABR")
    assert lon == -98.413333
    assert lat == 45.455833


@pytest.mark.parametrize(
    ("start_time", "end_time", "expected"),
    [
        (None, None, True),  # No date filter => always available
        ("1991-01-01 00:00:00", "1993-01-01 00:00:00", False),
        ("1991-01-01 00:00:00", "1997-01-01 00:00:00", True),  # cross start_time
        ("2022-01-01 00:00:00", "2023-01-01 00:00:00", True),  # within
        ("2022-01-01 00:00:00", "2030-01-01 00:00:00", True),  # cross_end_time
    ],
)
def test_is_radar_available(start_time, end_time, expected):
    """Test is_radar_available checks the time coverage properly."""
    result = is_radar_available("NEXRAD", "KABR", start_time, end_time)
    assert result == expected

    # Check return always True if start_time=None and end_time=None
    assert is_radar_available("NEXRAD", "KABR", start_time=None, end_time=None)


@pytest.mark.parametrize("network", NETWORKS)
def test_get_network_filename_patterns(network):
    """Test get_network_filename_patterns returns the test pattern."""
    patterns = get_network_filename_patterns(network)
    assert isinstance(patterns, list)


@pytest.mark.parametrize("network", NETWORKS)
def test_get_directory_pattern_cloud(network):
    """Test get_directory_pattern for a cloud protocol (e.g. s3)."""
    pattern = get_directory_pattern(protocol="s3", network=network)
    assert isinstance(pattern, str)


@pytest.mark.parametrize("network", NETWORKS)
def test_get_directory_pattern_local(network):
    """Test get_directory_pattern for local protocol."""
    pattern = get_directory_pattern(protocol="file", network=network)
    assert isinstance(pattern, str)


def test_get_filesystem_s3():
    """Test get_filesystem returns an s3 fsspec filesystem."""
    fs = get_filesystem("s3")
    assert isinstance(fs, s3fs.S3FileSystem)
    assert fs.protocol[0] == "s3"
    assert fs.anon is True


# def test_get_filesystem_gcs():
#     """Test get_filesystem returns a gcs fsspec filesystem."""
#     fs = get_filesystem("gcs")
#     assert isinstance(fs, gcsfs.GCSFileSystem)
#     assert fs.project is None  # typically None for anon


def test_get_filesystem_local():
    """Test get_filesystem returns a local fsspec filesystem."""
    fs = get_filesystem("file")
    assert isinstance(fs, fsspec.implementations.local.LocalFileSystem)
    assert fs.protocol == ("file", "local")


def test_get_filesystem_not_implemented():
    """Test get_filesystem raises NotImplementedError for unknown protocol."""
    with pytest.raises(NotImplementedError):
        get_filesystem("ftp")


def test_get_bucket_prefix():
    """Test get_bucket_prefix."""
    prefix = get_bucket_prefix("s3")
    assert prefix == "s3://"

    prefix = get_bucket_prefix("local")
    assert prefix == ""

    with pytest.raises(NotImplementedError):
        get_bucket_prefix("ftp")

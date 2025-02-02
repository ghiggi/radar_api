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
"""This module test the check functions."""

import datetime
import os

import numpy as np
import pandas as pd
import pytest
import pytz

from radar_api.checks import (
    check_base_dir,
    check_date,
    check_download_protocol,
    check_network,
    check_protocol,
    check_radar,
    check_start_end_time,
    check_time,
    get_current_utc_time,
)


class TestCheckBaseDir:

    def test_valid_base_dir(self, tmp_path):
        """Test check_base_dir returns the directory string if it exists."""
        # tmp_path is a pathlib.Path for a temporary directory
        valid_dir = str(tmp_path)
        assert check_base_dir(valid_dir) == valid_dir

    def test_base_dir_pathlib_object(self, tmp_path):
        """Test check_base_dir accepts a Pathlib object."""
        base_dir_str = str(tmp_path)
        assert check_base_dir(tmp_path) == base_dir_str

    def test_non_string_base_dir_raises(self):
        """Test check_base_dir raises TypeError for invalid type."""
        with pytest.raises(TypeError, match="must be a string or a Pathlib object"):
            check_base_dir(123)

    def test_base_dir_remove_trailing_path_separator(self, tmp_path):
        """Test check_base_dir removes trailing path separator."""
        # Convert the Path object to string, add a trailing slash
        base_dir_str = str(tmp_path) + os.path.sep
        # The returned directory should be the same but without trailing slash
        assert check_base_dir(base_dir_str) == str(tmp_path), "Trailing path separator is not removed"

    def test_non_existent_directory_raises_error(self):
        """Test check_base_dir raises OSError for a non-existent path."""
        with pytest.raises(OSError, match="does not exist"):
            check_base_dir("some_random_non_existent_directory_path")

    def test_path_is_not_directory_raises_error(self, tmp_path):
        """Test check_base_dir raises OSError if path is not a directory."""
        # Create a file in the tmp_path
        file_path = tmp_path / "testfile.txt"
        file_path.touch()
        with pytest.raises(OSError, match="is not a directory"):
            check_base_dir(str(file_path))


class TestCheckProtocol:
    def test_valid_protocol(self):
        """Test check_protocol with a valid recognized protocol."""
        protocol = "s3"
        assert check_protocol(protocol) == "s3"

    def test_local_protocol_becomes_file(self):
        """Test check_protocol mapping 'local' to 'file'."""
        protocol = "local"
        assert check_protocol(protocol) == "file"

    def test_none_protocol(self):
        """Test check_protocol returns None if protocol is None."""
        assert check_protocol(None) is None

    def test_unrecognized_protocol_raises(self):
        """Test check_protocol raises ValueError for unknown protocol."""
        with pytest.raises(ValueError, match="Valid `protocol` are"):
            check_protocol("ftp")

    def test_non_string_protocol_raises(self):
        """Test check_protocol raises TypeError for non-string protocol."""
        with pytest.raises(TypeError, match="must be a string"):
            check_protocol(123)


class TestCheckDownloadProtocol:

    def test_valid_download_protocol(self):
        """Test check_download_protocol with valid 's3'."""
        check_download_protocol("s3")

    def test_invalid_download_protocol_raises(self):
        """Test check_download_protocol raises ValueError for invalid protocol."""
        with pytest.raises(ValueError, match="Please specify either 'gcs' or 's3'"):
            check_download_protocol("ftp")


def test_check_network() -> None:
    """Test check_radar()."""
    # Test types that aren't strings
    for network in [123, None]:
        with pytest.raises(TypeError):
            check_network(network)

    # Test radar that does exist
    assert check_network("NEXRAD") == "NEXRAD"

    # Test a satellite that doesn't exist
    with pytest.raises(ValueError):
        check_network("DUMMY")


def test_check_radar() -> None:
    """Test check_radar()."""
    # Test types that aren't strings
    for radar in [123, None]:
        with pytest.raises(TypeError):
            check_radar(radar, network="NEXRAD")

    # Test radar that does exist
    assert check_radar("KLIX", network="NEXRAD") == "KLIX"

    # Test a satellite that doesn't exist
    with pytest.raises(ValueError):
        check_radar("DUMMY", network="NEXRAD")


def test_check_time() -> None:
    """Test that time is returned a `datetime.datetime` object from varying inputs."""
    # Test a string
    res = check_time("2014-12-31")
    assert isinstance(res, datetime.datetime)
    assert res == datetime.datetime(2014, 12, 31)

    # Test a string with hh/mm/ss
    res = check_time("2014-12-31 12:30:30")
    assert isinstance(res, datetime.datetime)
    assert res == datetime.datetime(2014, 12, 31, 12, 30, 30)

    # Test a string with <date>T<time>
    res = check_time("2014-12-31T12:30:30")
    assert isinstance(res, datetime.datetime)
    assert res == datetime.datetime(2014, 12, 31, 12, 30, 30)

    # Test a datetime object
    res = check_time(datetime.datetime(2014, 12, 31))
    assert isinstance(res, datetime.datetime)
    assert res == datetime.datetime(2014, 12, 31)

    # Test a datetime timestamp with h/m/s/ms
    res = check_time(datetime.datetime(2014, 12, 31, 12, 30, 30, 300))
    assert isinstance(res, datetime.datetime)
    assert res == datetime.datetime(2014, 12, 31, 12, 30, 30, 300)

    # Test a numpy.datetime64 object of "datetime64[s]"
    res = check_time(np.datetime64("2014-12-31"))
    assert isinstance(res, datetime.datetime)
    assert res == datetime.datetime(2014, 12, 31)

    # Test a object of datetime64[ns] casts to datetime64[ms]
    res = check_time(np.datetime64("2014-12-31T12:30:30.934549845", "s"))
    assert isinstance(res, datetime.datetime)
    assert res == datetime.datetime(2014, 12, 31, 12, 30, 30)

    # Test a datetime.date
    res = check_time(datetime.date(2014, 12, 31))
    assert isinstance(res, datetime.datetime)
    assert res == datetime.datetime(2014, 12, 31)

    # Test a datetime object inside a numpy array
    with pytest.raises(ValueError):
        res = check_time(np.array([datetime.datetime(2014, 12, 31, 12, 30, 30)]))

    # Test a pandas Timestamp object inside a numpy array
    with pytest.raises(ValueError):
        res = check_time(np.array([pd.Timestamp("2014-12-31 12:30:30")]))

    # Test a pandas Timestamp object
    res = check_time(pd.Timestamp("2014-12-31 12:30:30"))
    assert isinstance(res, datetime.datetime)
    assert res == datetime.datetime(2014, 12, 31, 12, 30, 30)

    # Test automatic casting to seconds accuracy
    res = check_time(np.datetime64("2014-12-31T12:30:30.934549845", "ns"))
    assert res == datetime.datetime(2014, 12, 31, 12, 30, 30)

    # Test a non isoformat string
    with pytest.raises(ValueError):
        check_time("2014/12/31")

    # Test a non datetime object
    with pytest.raises(TypeError):
        check_time(123)

    # Check numpy single timestamp
    res = check_time(np.array(["2014-12-31"], dtype="datetime64[s]"))
    assert isinstance(res, datetime.datetime)
    assert res == datetime.datetime(2014, 12, 31)

    # Check numpy multiple timestamp
    with pytest.raises(ValueError):
        check_time(np.array(["2014-12-31", "2015-01-01"], dtype="datetime64[s]"))

    # Test with numpy non datetime64 object
    with pytest.raises(ValueError):
        check_time(np.array(["2014-12-31"]))

    # Check non-UTC timezone
    for timezone in ["Europe/Zurich", "Australia/Melbourne"]:
        with pytest.raises(ValueError):
            check_time(
                datetime.datetime(2014, 12, 31, 12, 30, 30, 300, tzinfo=pytz.timezone(timezone)),
            )

    # Check UTC timezone info is removed
    res = check_time(datetime.datetime(2014, 12, 31, 12, 30, 30, 300, tzinfo=pytz.utc))
    assert isinstance(res.tzinfo, type(None))


def test_check_date() -> None:
    """Check if `datetime.date` object is returned from varying inputs."""
    # Test a datetime object
    res = check_date(datetime.datetime(2014, 12, 31))
    assert isinstance(res, datetime.date)
    assert res == datetime.date(2014, 12, 31)

    # Test a datetime timestamp with h/m/s/ms
    res = check_date(datetime.datetime(2014, 12, 31, 12, 30, 30, 300))
    assert isinstance(res, datetime.date)
    assert res == datetime.date(2014, 12, 31)

    # Test a string is cast to date
    res = check_date("2014-12-31")
    assert isinstance(res, datetime.date)
    assert res == datetime.date(2014, 12, 31)

    # Test a np datetime object is cast to date
    res = check_date(np.datetime64("2014-12-31"))
    assert res == datetime.date(2014, 12, 31)
    assert isinstance(res, datetime.date)

    # Test None raises exception
    with pytest.raises(TypeError):
        check_date(None)


def test_check_start_end_time() -> None:
    """Check start and end time are valid."""
    # Test a string
    res = check_start_end_time(
        "2014-12-31",
        "2015-01-01",
    )
    assert isinstance(res, tuple)

    # Test the reverse for exception
    with pytest.raises(ValueError):
        check_start_end_time(
            "2015-01-01",
            "2014-12-31",
        )

    # Test a datetime object
    res = check_start_end_time(
        datetime.datetime(2014, 12, 31),
        datetime.datetime(2015, 1, 1),
    )
    assert isinstance(res, tuple)

    # Test the reverse datetime object for exception
    with pytest.raises(ValueError):
        check_start_end_time(
            datetime.datetime(2015, 1, 1),
            datetime.datetime(2014, 12, 31),
        )

    # Test a datetime timestamp with h/m/s/ms
    res = check_start_end_time(
        datetime.datetime(2014, 12, 31, 12, 30, 30, 300),
        datetime.datetime(2015, 1, 1, 12, 30, 30, 300),
    )

    # Test end time in the future
    # with pytest.raises(ValueError):
    #     check_start_end_time(
    #         datetime.datetime(2014, 12, 31, 12, 30, 30, 300),
    #         datetime.datetime(2125, 1, 1, 12, 30, 30, 300),
    #     )

    # Test start time in the future
    with pytest.raises(ValueError):
        check_start_end_time(
            datetime.datetime(2125, 12, 31, 12, 30, 30, 300),
            datetime.datetime(2126, 1, 1, 12, 30, 30, 300),
        )

    # Test endtime in UTC. This should pass as UTC time generated in the test is slightly
    # behind the current time tested in the function
    check_start_end_time(
        datetime.datetime(2014, 12, 31, 12, 30, 30, 300),
        get_current_utc_time(),
    )

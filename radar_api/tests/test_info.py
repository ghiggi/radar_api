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
"""This module test the info extraction from radar filename."""

import datetime

import pytest

from radar_api.info import (
    FILE_KEYS,
    TIME_KEYS,
    check_groups,
    get_end_time_from_filepaths,
    get_info_from_filename,
    get_info_from_filepath,
    get_key_from_filepath,
    get_key_from_filepaths,
    get_season,
    get_start_end_time_from_filepaths,
    get_start_time_from_filepaths,
    get_time_component,
    get_version_from_filepaths,
    group_filepaths,
)

SAMPLE_FILES = {
    # <network> : [<sample_filenames>]
    "FMI": ["202101010100_fiika_PVOL.h5"],
    "NEXRAD": ["KFSX19960701_044028.gz", "KABR20100101_000618_V03", "KLIX20211220_160243_V06"],
    "IDEAM": ["9100SAN-20240202-105624-PPIVol-0d1c.nc", "BAR240201135316.RAWMUAK"],
}


#### Examples info dictionaries


SAMPLE_FILES_INFO_DICT = {
    "FMI": [
        # Filename
        (
            "202101010100_fiika_PVOL.h5",
            # InfoDict
            {
                "start_time": datetime.datetime(2021, 1, 1, 1, 0),
                "end_time": None,
                "radar_acronym": "fiika",
                "volume_identifier": "PVOL",
                "extension": "h5",
                "version": "",
            },
        ),
    ],
    "NEXRAD": [
        # Filename
        (
            "KFSX19960701_044028.gz",
            # InfoDict
            {
                "start_time": datetime.datetime(1996, 7, 1, 4, 40, 28),
                "end_time": None,
                "radar_acronym": "KFSX",
                "volume_identifier": "",
                "extension": "gz",
                "version": "",
            },
        ),
        # Filename
        (
            "KABR20100101_000618_V03.gz",
            # InfoDict
            {
                "start_time": datetime.datetime(2010, 1, 1, 0, 6, 18),
                "end_time": None,
                "radar_acronym": "KABR",
                "volume_identifier": "",
                "extension": "gz",
                "version": "3",
            },
        ),
        (
            "KABR20100101_000618_V06",
            # InfoDict
            {
                "start_time": datetime.datetime(2010, 1, 1, 0, 6, 18),
                "end_time": None,
                "radar_acronym": "KABR",
                "volume_identifier": "",
                "extension": "",
                "version": "6",
            },
        ),
    ],
    "IDEAM": [
        (
            # Filename
            "9100SAN-20240202-105624-PPIVol-0d1c.nc",
            # InfoDict
            {
                "start_time": datetime.datetime(2024, 2, 2, 10, 56, 24),
                "end_time": None,
                "radar_acronym": "9100SAN",
                "volume_identifier": "0d1c",
                "extension": "nc",
                "version": "",
            },
        ),
        # Filename
        (
            "BAR240201135316.RAWMUAK",
            # InfoDict
            {
                "start_time": datetime.datetime(2024, 2, 1, 13, 53, 16),
                "end_time": None,
                "radar_acronym": "BAR",
                "volume_identifier": "MUAK",
                "extension": "",
                "version": "",
            },
        ),
    ],
}


NETWORKS = list(SAMPLE_FILES)


##############################
# Helper to parametrize tests
##############################


def _generate_test_params(sample_dict):
    """Generate (network, filename, expected_info) for all samples in SAMPLE_FILES_INFO_DICT."""
    for network, file_info_list in sample_dict.items():
        for filename, expected_info in file_info_list:
            test_id = f"{network}-{filename}"
            yield pytest.param(network, filename, expected_info, id=test_id)


####------------------------------------------------------------------------


@pytest.mark.parametrize(("network", "filename", "expected_info"), _generate_test_params(SAMPLE_FILES_INFO_DICT))
def test_get_info_from_filename(network, filename, expected_info):
    """Test get_info_from_filename returns the correct parsed info for known filenames."""
    parsed_info = get_info_from_filename(filename, network)
    # Check each key in expected_info
    for key, expected_val in expected_info.items():
        assert parsed_info.get(key) == expected_val, (
            f"For '{filename}', key '{key}' should be {expected_val}, " f"but got {parsed_info.get(key)}"
        )
    # Check that no unexpected keys exist
    extra_keys = set(parsed_info.keys()) - set(expected_info.keys())
    assert len(extra_keys) == 0, f"Extra keys: {extra_keys}"


def test_get_info_from_invalid_filename():
    """Test get_info_from_filename raise error or return empty dictionary for unknown filenames."""
    with pytest.raises(ValueError):
        get_info_from_filename("invalid_filename", network="NEXRAD")

    # Assert that if ignore_errors = True, return empty dictionary
    assert get_info_from_filename("invalid_filename", network="NEXRAD", ignore_errors=True) == {}


def test_get_info_from_invalid_filepath():
    """Test get_info_from_filepath raise error with invalid filepaths."""
    # Invalid filename
    with pytest.raises(ValueError):
        get_info_from_filepath("invalid_filename", network="NEXRAD")

    # Filepath not a string
    with pytest.raises(TypeError):
        get_info_from_filepath(123, network="NEXRAD")

    # Assert that if ignore_errors = True, return empty dictionary
    assert get_info_from_filepath("invalid_filename", network="NEXRAD", ignore_errors=True) == {}


@pytest.mark.parametrize(("network", "filename", "expected_info"), _generate_test_params(SAMPLE_FILES_INFO_DICT))
def test_get_key_from_filepath_valid(network, filename, expected_info):
    """Test get_key_from_filepath returns the requested key value."""
    for key, expected_val in expected_info.items():
        # Some keys might be None in expected_info, skip them or test them if relevant
        returned_val = get_key_from_filepath(filename, key=key, network=network)
        assert returned_val == expected_val, f"For key '{key}', expected {expected_val} but got {returned_val}"


def test_get_key_from_filepath_missing_key():
    """Test get_key_from_filepath raises KeyError if requested key is not present."""
    with pytest.raises(KeyError):
        get_key_from_filepath("KFSX19960701_044028.gz", key="non_existent", network="NEXRAD")


def test_get_key_from_filepaths():
    """Test get_key_from_filepaths returns a list of the requested key value."""
    filepaths = ["202101010100_fiika_PVOL.h5"]
    # Test input a list return a list
    assert isinstance(get_key_from_filepaths(filepaths, network="FMI", key="start_time"), list)
    # Test input a string return still a list
    assert isinstance(get_key_from_filepaths(filepaths[0], network="FMI", key="start_time"), list)


def test_get_start_time_from_filepaths() -> None:
    """Test that the start time is correctly extracted from filepaths."""
    # We'll use the FMI sample as an example
    filenames = ["202101010100_fiika_PVOL.h5"]
    times = get_start_time_from_filepaths(filenames, network="FMI")
    # The function returns a list, so check the first item
    assert len(times) == 1
    assert times[0] == datetime.datetime(2021, 1, 1, 1, 0)


def test_get_end_time_from_filepaths() -> None:
    """Test that the end time is correctly extracted from filepaths."""
    # We'll use the FMI sample as an example (without end_time in filename)
    filenames = ["202101010100_fiika_PVOL.h5"]
    times = get_end_time_from_filepaths(filenames, network="FMI")
    assert len(times) == 1
    assert times[0] is None, f"Expected None end_time for {filenames[0]}"


def test_get_start_end_time_from_filepaths() -> None:
    """Test get_start_end_time_from_filepaths returns numpy arrays."""
    filenames = ["202101010100_fiika_PVOL.h5"]
    start_arr, end_arr = get_start_end_time_from_filepaths(filenames, network="FMI")
    assert len(start_arr) == 1
    assert len(end_arr) == 1
    assert start_arr[0] == datetime.datetime(2021, 1, 1, 1, 0)
    assert end_arr[0] is None
    assert hasattr(start_arr, "shape")
    assert hasattr(end_arr, "shape"), "Expected numpy arrays."


def test_get_versions_from_filepaths() -> None:
    """Test that the version is correctly extracted from filepaths."""
    filenames = ["KFSX19960701_044028.gz", "KABR20100101_000618_V03.gz", "KABR20100101_000618_V06"]
    output_version = get_version_from_filepaths(filenames, network="NEXRAD")
    assert output_version == [None, 3, 6]

    assert get_version_from_filepaths(filenames[0], network="NEXRAD") == [None]  # input str output list


def test_check_groups():
    """Test check_groups function."""
    valid_groups = ["radar_acronym", "volume_identifier", "version", "extension"]
    assert check_groups(valid_groups) == valid_groups

    invalid_groups = ["invalid1", "invalid2"]
    with pytest.raises(ValueError):
        check_groups(invalid_groups)

    with pytest.raises(TypeError):
        check_groups(1)


def test_get_time_component():
    """Test get_time_component function."""
    start_time = datetime.datetime(2020, 2, 1, 2, 3, 4)
    assert get_time_component(start_time, "year") == "2020"
    assert get_time_component(start_time, "month") == "2"
    assert get_time_component(start_time, "day") == "1"
    assert get_time_component(start_time, "doy") == "32"
    assert get_time_component(start_time, "dow") == "5"
    assert get_time_component(start_time, "hour") == "2"
    assert get_time_component(start_time, "minute") == "3"
    assert get_time_component(start_time, "second") == "4"
    assert get_time_component(start_time, "month_name") == "February"
    assert get_time_component(start_time, "quarter") == "1"
    assert get_time_component(start_time, "season") == "DJF"


def test_get_season():
    """Test get_season function."""
    assert get_season(datetime.datetime(2020, 1, 1)) == "DJF"
    assert get_season(datetime.datetime(2020, 4, 1)) == "MAM"
    assert get_season(datetime.datetime(2020, 7, 1)) == "JJA"
    assert get_season(datetime.datetime(2020, 10, 1)) == "SON"


@pytest.mark.parametrize("network", NETWORKS)
def test_group_filepaths(network):
    """Test group_filepaths function."""
    filepaths = SAMPLE_FILES[network]

    # Test groups = None
    assert group_filepaths(filepaths, None) == filepaths

    # Test all time keys pass
    for key in TIME_KEYS:
        assert isinstance(group_filepaths(filepaths, network=network, groups=key), dict)

    # Test multiple groups
    assert isinstance(group_filepaths([filepaths[0]], network=network, groups=["radar_acronym", "year", "month"]), dict)

    # Test all file keys pass
    for key in FILE_KEYS:
        assert isinstance(group_filepaths(filepaths, network=network, groups=key), dict)


def test_group_filepaths_by_time():
    """Test group_filepaths by time."""
    network = "NEXRAD"
    dummy_filepath = "KABR20100101_000618_V03"

    # Test single group
    assert group_filepaths([dummy_filepath], network=network, groups="year") == {"2010": [dummy_filepath]}

    # Test multiple groups
    assert group_filepaths([dummy_filepath], network=network, groups=["radar_acronym", "year", "month"]) == {
        "KABR/2010/1": [dummy_filepath],
    }

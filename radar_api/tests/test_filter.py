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
"""This module test the file filtering routines."""
from radar_api.filter import (
    is_file_within_time,
    # filter_file,
    # filter_files,
)


def test_is_file_within_time() -> None:
    """Test is_file_within_time()."""
    # Set a file time 01.01.14 01:00 to 04:00 (start, end)
    file_time = ("2014-01-01T01:00:00Z", "2014-01-01T04:00:00Z")

    # Test True assumptions
    true_assumptions = [
        ("2014-01-01T00:00:00Z", "2014-01-01T05:00:00Z"),  # Crosses start
        ("2014-01-01T02:00:00Z", "2014-01-01T03:00:00Z"),  # Within
        ("2014-01-01T03:00:00Z", "2014-01-01T05:00:00Z"),  # Crosses end
    ]

    for start_time, end_time in true_assumptions:
        assert (
            is_file_within_time(
                start_time=start_time,
                end_time=end_time,
                file_start_time=file_time[0],
                file_end_time=file_time[1],
            )
            is True
        )

    # Test `False` assumptions
    false_assumptions = [
        ("2014-01-01T00:00:00Z", "2014-01-01T00:01:01Z"),  # Ends at start
        ("2013-01-01T00:00:00Z", "2013-01-01T05:00:00Z"),  # Before start
        ("2014-01-01T00:00:00Z", "2014-01-01T00:59:59Z"),  # Before start
        ("2014-01-01T05:00:00Z", "2014-01-01T06:00:00Z"),  # After end
        ("2014-01-01T04:00:00Z", "2014-01-01T05:00:00Z"),  # Starts at end
    ]

    for start_time, end_time in false_assumptions:
        assert (
            is_file_within_time(
                start_time=start_time,
                end_time=end_time,
                file_start_time=file_time[0],
                file_end_time=file_time[1],
            )
            is False
        )

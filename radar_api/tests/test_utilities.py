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
"""Tests for geospatial radar utility helpers."""

import pytest

from radar_api.utilities import (
    available_radars_around_point,
    available_radars_within_extent,
    read_database,
)


def test_read_database():
    """Test read_database returns a radar metadata DataFrame."""
    db = read_database(network="NEXRAD")
    assert len(db) > 0
    assert {"network", "radar", "longitude", "latitude"}.issubset(db.columns)
    row = db.loc[db["radar"] == "KABR"].iloc[0]
    assert row["network"] == "NEXRAD"
    assert row["longitude"] == -98.413333
    assert row["latitude"] == 45.455833


def test_available_radars_around_point():
    """Test search around a point using a tight search radius."""
    point = (-98.413333, 45.455833)
    radars = available_radars_around_point(point=point, distance=1, network="NEXRAD")
    assert ("NEXRAD", "KABR") in radars
    assert all(network == "NEXRAD" for network, _ in radars)


def test_available_radars_around_point_return_distance():
    """Test search around a point optionally returns the distance."""
    point = (-98.413333, 45.455833)
    radars = available_radars_around_point(
        point=point,
        distance=1,
        network="NEXRAD",
        return_distance=True,
    )
    assert ("NEXRAD", "KABR", 0.0) in radars
    assert all(network == "NEXRAD" for network, _, _ in radars)


def test_available_radars_around_point_return_radar_location():
    """Test search around a point optionally returns the radar location."""
    point = (-98.413333, 45.455833)
    radars = available_radars_around_point(
        point=point,
        distance=1,
        network="NEXRAD",
        return_radar_location=True,
    )
    assert ("NEXRAD", "KABR", (-98.413333, 45.455833)) in radars
    assert all(network == "NEXRAD" for network, _, _ in radars)


def test_available_radars_around_point_return_distance_and_radar_location():
    """Test search around a point optionally returns distance and radar location."""
    point = (-98.413333, 45.455833)
    radars = available_radars_around_point(
        point=point,
        distance=1,
        network="NEXRAD",
        return_distance=True,
        return_radar_location=True,
    )
    assert ("NEXRAD", "KABR", 0.0, (-98.413333, 45.455833)) in radars
    assert all(network == "NEXRAD" for network, _, _, _ in radars)


def test_available_radars_around_point_no_match():
    """Test search around a point far from any NEXRAD radar."""
    radars = available_radars_around_point(point=(0, 0), distance=1000, network="NEXRAD")
    assert radars == []


def test_available_radars_within_extent():
    """Test search within a small extent around KABR."""
    extent = (-98.42, -98.40, 45.45, 45.46)
    radars = available_radars_within_extent(extent=extent, network="NEXRAD")
    assert ("NEXRAD", "KABR") in radars
    assert all(network == "NEXRAD" for network, _ in radars)


def test_available_radars_around_point_negative_distance():
    """Test negative distance is rejected."""
    with pytest.raises(ValueError, match="greater than or equal to 0"):
        available_radars_around_point(point=(0, 0), distance=-1)


def test_available_radars_within_extent_invalid_extent():
    """Test extent with invalid latitude ordering is rejected."""
    with pytest.raises(ValueError, match="lat_min <= lat_max"):
        available_radars_within_extent(extent=(-10, 10, 5, -5))

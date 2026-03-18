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
"""Geospatial utilities to search available radars."""

import numpy as np
import pandas as pd

from radar_api.io import available_networks, available_radars, get_radar_info


def _normalize_point(point):
    """Validate and normalize a ``(lon, lat)`` point."""
    if isinstance(point, str):
        raise TypeError("`point` must be an iterable with `(lon, lat)` coordinates.")

    try:
        point = tuple(float(value) for value in point)
    except TypeError as exc:
        raise TypeError("`point` must be an iterable with `(lon, lat)` coordinates.") from exc
    except ValueError as exc:
        raise ValueError("`point` coordinates must be numeric.") from exc

    if len(point) != 2:
        raise ValueError("`point` must contain exactly two values: `(lon, lat)`.")

    lon, lat = point
    if not -180 <= lon <= 180:
        raise ValueError("`point` longitude must be between -180 and 180 degrees.")
    if not -90 <= lat <= 90:
        raise ValueError("`point` latitude must be between -90 and 90 degrees.")
    return lon, lat


def _normalize_distance(distance):
    """Validate and normalize a distance in meters."""
    try:
        distance = float(distance)
    except (TypeError, ValueError) as exc:
        raise TypeError("`distance` must be a numeric value expressed in meters.") from exc

    if distance < 0:
        raise ValueError("`distance` must be greater than or equal to 0 meters.")
    return distance


def _normalize_extent(extent):
    """Validate and normalize a geographic extent."""
    if isinstance(extent, str):
        raise TypeError(
            "`extent` must be an iterable with `(lon_min, lon_max, lat_min, lat_max)` coordinates.",
        )

    try:
        extent = tuple(float(value) for value in extent)
    except TypeError as exc:
        raise TypeError(
            "`extent` must be an iterable with `(lon_min, lon_max, lat_min, lat_max)` coordinates.",
        ) from exc
    except ValueError as exc:
        raise ValueError("`extent` coordinates must be numeric.") from exc

    if len(extent) != 4:
        raise ValueError(
            "`extent` must contain exactly four values: `(lon_min, lon_max, lat_min, lat_max)`.",
        )

    lon_min, lon_max, lat_min, lat_max = extent
    if not -180 <= lon_min <= 180 or not -180 <= lon_max <= 180:
        raise ValueError("`extent` longitudes must be between -180 and 180 degrees.")
    if not -90 <= lat_min <= 90 or not -90 <= lat_max <= 90:
        raise ValueError("`extent` latitudes must be between -90 and 90 degrees.")
    if lat_min > lat_max:
        raise ValueError("`extent` requires `lat_min <= lat_max`.")
    return lon_min, lon_max, lat_min, lat_max


def read_database(network=None):
    """Return a DataFrame summarizing radar metadata.

    Parameters
    ----------
    network : str, optional
        Radar network name. If ``None``, retrieve radar metadata for all
        available networks.

    Returns
    -------
    pandas.DataFrame
        DataFrame with one row per radar. Columns are the union of the keys
        available across the radar configuration files, plus ``network`` and
        ``radar``.
    """
    networks = available_networks() if network is None else [network]

    records = []
    for current_network in networks:
        for radar in available_radars(network=current_network):
            record = {
                "network": current_network,
                "radar": radar,
            }
            record.update(get_radar_info(network=current_network, radar=radar))
            records.append(record)

    if len(records) == 0:
        return pd.DataFrame(columns=["network", "radar"])
    return pd.DataFrame.from_records(records)


def _get_radar_location_database(network=None):
    """Return a DataFrame with numeric longitude and latitude columns."""
    db = read_database(network=network).copy()
    if len(db) == 0:
        return db

    if "longitude" not in db.columns or "latitude" not in db.columns:
        raise ValueError("Radar location not available.")

    db["longitude"] = pd.to_numeric(db["longitude"], errors="coerce")
    db["latitude"] = pd.to_numeric(db["latitude"], errors="coerce")

    if db[["longitude", "latitude"]].isna().any().any():
        raise ValueError("Radar location not available.")
    return db


def _get_geod():
    """Return the WGS84 geodesic calculator."""
    from pyproj import Geod

    return Geod(ellps="WGS84")


def _is_longitude_within_extent(lon, lon_min, lon_max):
    """Check if a longitude falls within an extent, including dateline crossing."""
    if lon_min <= lon_max:
        return lon_min <= lon <= lon_max
    return lon >= lon_min or lon <= lon_max


def available_radars_around_point(
    point,
    distance,
    network=None,
    return_distance=False,
    return_radar_location=False,
):
    """Return radars within a geodesic distance from a ``(lon, lat)`` point.

    Parameters
    ----------
    point : tuple or list
        Geographic point as ``(lon, lat)`` in degrees.
    distance : float
        Search radius in meters.
    network : str, optional
        Radar network name. If ``None``, search across all available networks.
    return_distance : bool, optional
        If ``True``, also return the geodesic distance in meters as
        ``(network, radar, distance)``.
    return_radar_location : bool, optional
        If ``True``, also return the radar location as ``(lon, lat)``.

    Returns
    -------
    list[tuple]
        List of ``(network, radar)`` tuples, optionally extended with
        ``distance`` and ``(lon, lat)`` depending on the selected flags.
    """
    lon, lat = _normalize_point(point)
    distance = _normalize_distance(distance)

    db = _get_radar_location_database(network=network)
    if len(db) == 0:
        return []

    lons = db["longitude"].to_numpy(dtype=float)
    lats = db["latitude"].to_numpy(dtype=float)

    geod = _get_geod()
    _, _, distances = geod.inv(
        lons,
        lats,
        np.full(lons.shape, lon, dtype=float),
        np.full(lats.shape, lat, dtype=float),
        radians=False,
    )
    distances = np.asarray(distances, dtype=float)

    matches = []
    for row, radar_distance in zip(db.itertuples(index=False), distances, strict=False):
        if radar_distance <= distance:
            match = [row.network, row.radar]
            if return_distance:
                match.append(float(radar_distance))
            if return_radar_location:
                match.append((float(row.longitude), float(row.latitude)))
            matches.append(tuple(match))
    return matches


def available_radars_within_extent(extent, network=None):
    """Return radars whose location falls within a geographic extent.

    Parameters
    ----------
    extent : tuple or list
        Geographic extent as ``(lon_min, lon_max, lat_min, lat_max)`` in degrees.
        Extents crossing the antimeridian are supported by specifying
        ``lon_min > lon_max``.
    network : str, optional
        Radar network name. If ``None``, search across all available networks.

    Returns
    -------
    list[tuple[str, str]]
        List of ``(network, radar)`` tuples.
    """
    lon_min, lon_max, lat_min, lat_max = _normalize_extent(extent)

    db = _get_radar_location_database(network=network)
    if len(db) == 0:
        return []

    valid_longitude = db["longitude"].apply(_is_longitude_within_extent, args=(lon_min, lon_max))
    valid_latitude = (db["latitude"] >= lat_min) & (db["latitude"] <= lat_max)
    subset = db.loc[valid_longitude & valid_latitude, ["network", "radar"]]
    return list(subset.itertuples(index=False, name=None))

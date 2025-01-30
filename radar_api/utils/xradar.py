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
"""This module include xradar utilities."""
import numpy as np
import xarray as xr


def _get_field_array(radar_obj, sweep, field_name):
    masked_arr = radar_obj.get_field(sweep=sweep, field_name=field_name)
    arr = masked_arr.data
    arr[masked_arr.mask] = np.nan
    return arr


def _get_radar_location(radar_obj):
    # Retrieve radar site location
    dict_loc = {}
    dict_loc["latitude"] = float(radar_obj.latitude["data"][0])
    dict_loc["longitude"] = float(radar_obj.longitude["data"][0])
    dict_loc["altitude"] = float(radar_obj.altitude["data"][0])
    return dict_loc


def _get_sweep_dataset(radar_obj, sweep):
    dict_da = {}
    fields = list(radar_obj.fields)
    for field_name in fields:
        arr = _get_field_array(radar_obj, sweep, field_name)
        dims = radar_obj.fields[field_name]["coordinates"].split(" ")[1:]
        dict_da[field_name] = xr.DataArray(arr, dims=dims)
    ds = xr.Dataset(dict_da)
    # Add coords
    coords_dict = {
        "azimuth": ("azimuth", radar_obj.get_azimuth(sweep)),
        "elevation": ("azimuth", radar_obj.get_elevation(sweep)),
        "range": ("range", radar_obj.range["data"][: ds.sizes["range"]]),
        "time": ("azimuth", radar_obj.time["data"][radar_obj.get_slice(sweep)]),
    }
    # Add other coordinates
    coords_dict.update(_get_radar_location(radar_obj))
    coords_dict["sweep_number"] = sweep
    coords_dict["sweep_mode"] = radar_obj.sweep_mode["data"][sweep]
    coords_dict["sweep_fixed_angle"] = radar_obj.fixed_angle["data"][sweep]

    ds = ds.assign_coords(coords_dict)
    ds["time"].attrs["units"] = radar_obj.time["units"]

    # Decode time
    ds = xr.decode_cf(ds, decode_times=True)
    return ds


def get_nexrad_datatree_from_pyart(radar_obj):
    """Convert a pyart object to xradar datatree."""
    # Define renaming dictionary to CF-Radials2
    # --> https://github.com/openradar/xradar/blob/830d86b1c6290f1dce0e73c60a1d3b819735f906/xradar/model.py#L385
    # --> Currently set same range for all sweeps !
    # --> Currently do not copy metadata and variable attributes !
    dict_var_naming = {
        "reflectivity": "DBZH",
        "differential_reflectivity": "ZDR",
        "cross_correlation_ratio": "RHOHV",
        "differential_phase": "PHIDP",
        "spectrum_width": "WRADH",
        "velocity": "VRADH",
        # 'clutter_filter_power_removed',
    }
    dict_ds = {}
    for sweep in radar_obj.sweep_number["data"]:
        sweep_name = f"sweep_{sweep}"
        ds = _get_sweep_dataset(radar_obj, sweep=sweep)
        dict_ds[sweep_name] = ds.rename(dict_var_naming)
    dt = xr.DataTree.from_dict(dict_ds)
    # Add geolocation
    for coord, value in _get_radar_location(radar_obj).items():
        dt[coord] = value

    return dt

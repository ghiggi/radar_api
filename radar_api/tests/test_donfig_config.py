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
"""Check RADAR-API configuration files."""
import os  # noqa

import pytest
from unittest import mock


def test_donfig_takes_environment_variable():
    """Test that the donfig config file takes the environment defaults."""
    from importlib import reload

    import radar_api

    with mock.patch.dict("os.environ", {"RADAR_BASE_DIR": "/my_path_to/RADAR"}):
        reload(radar_api._config)
        reload(radar_api)
        assert radar_api.config.get("base_dir") == "/my_path_to/RADAR"


def test_donfig_takes_config_yaml_file(tmp_path, mocker):
    """Test that the donfig config file takes the YAML defaults."""
    from importlib import reload

    import radar_api

    # Mock to save config YAML at custom location
    config_fpath = str(tmp_path / ".config_radar_api_api.yaml")
    mocker.patch("radar_api.configs._define_config_filepath", return_value=config_fpath)

    # Initialize config YAML
    radar_api.configs.define_configs(base_dir="test_dir/RADAR")

    reload(radar_api._config)
    reload(radar_api)
    assert radar_api.config.get("base_dir") == "test_dir/RADAR"


CONFIGS_TEST_KWARGS = {
    "base_dir": "test_base_dir",
}


@pytest.mark.parametrize("key_value", list(CONFIGS_TEST_KWARGS.items()))
def test_donfig_context_manager(key_value):
    """Test that the donfig context manager works as expected."""
    import radar_api

    key = key_value[0]
    value = key_value[1]

    # Assert donfig key context manager
    with radar_api.config.set({key: value}):
        assert radar_api.config.get(key) == value

    # # Assert if not initialized, defaults to None
    # assert radar_api.config.get(key) is None

    # Now initialize
    radar_api.config.set({key: value})
    assert radar_api.config.get(key) == value

    # Now try context manager again
    with radar_api.config.set({key: "new_value"}):
        assert radar_api.config.get(key) == "new_value"
    assert radar_api.config.get(key) == value

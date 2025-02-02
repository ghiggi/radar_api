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
import os

import pytest

CONFIGS_TEST_KWARGS = {
    "base_dir": "test_base_dir",
}


def test_define_configs(tmp_path, mocker):
    """Test define_configs function."""
    import radar_api

    # Mock to save config YAML at custom location
    config_filepath = str(tmp_path / ".config_radar_api_api.yaml")
    mocker.patch("radar_api.configs._define_config_filepath", return_value=config_filepath)

    # Define config YAML
    radar_api.configs.define_configs(**CONFIGS_TEST_KWARGS)
    assert os.path.exists(tmp_path / ".config_radar_api_api.yaml")


def test_read_configs(tmp_path, mocker):
    """Test read_configs function."""
    from radar_api.configs import define_configs, read_configs

    # Mock to save config YAML at custom location
    config_filepath = str(tmp_path / ".config_radar_api_api.yaml")
    mocker.patch("radar_api.configs._define_config_filepath", return_value=config_filepath)

    # Define config YAML
    define_configs(**CONFIGS_TEST_KWARGS)
    assert os.path.exists(tmp_path / ".config_radar_api_api.yaml")

    # Read config YAML
    config_dict = read_configs()
    assert isinstance(config_dict, dict)
    print(config_dict)
    assert config_dict["base_dir"] == "test_base_dir"


def test_update_radar_api_configs(tmp_path, mocker):
    """Test define_configs function in 'update' mode."""
    import radar_api
    from radar_api.utils.yaml import read_yaml

    # Mock to save config YAML at custom location
    config_filepath = str(tmp_path / ".config_radar_api_api.yaml")
    mocker.patch("radar_api.configs._define_config_filepath", return_value=config_filepath)

    # Initialize
    radar_api.configs.define_configs(**CONFIGS_TEST_KWARGS)
    assert os.path.exists(config_filepath)

    # Read
    config_dict = read_yaml(config_filepath)
    assert config_dict["base_dir"] == "test_base_dir"

    # Update
    radar_api.configs.define_configs(
        base_dir="new_test_base_dir",
    )
    assert os.path.exists(config_filepath)
    config_dict = read_yaml(config_filepath)
    assert config_dict["base_dir"] == "new_test_base_dir"


def test_get_base_dir():
    """Test get_base_dir function."""
    import radar_api
    from radar_api.configs import get_base_dir

    # Check that if input is not None, return the specified base_dir
    assert get_base_dir(base_dir="test/radar_api") == "test/radar_api"

    # Check that if no config YAML file specified (base_dir=None), raise error
    with radar_api.config.set({"base_dir": None}), pytest.raises(ValueError):
        get_base_dir()

    # Set base_dir in the donfig config and check it return it !
    radar_api.config.set({"base_dir": "another_test_dir/radar_api"})
    assert get_base_dir() == "another_test_dir/radar_api"

    # Now test that return the one from the temporary radar_api.config donfig object
    with radar_api.config.set({"base_dir": "new_test_dir/radar_api"}):
        assert get_base_dir() == "new_test_dir/radar_api"

    # And check it return the default one
    assert get_base_dir() == "another_test_dir/radar_api"


@pytest.mark.parametrize("key_value", list(CONFIGS_TEST_KWARGS.items()))
def test_get_argument_value(key_value):
    import radar_api
    from radar_api import configs as configs_module

    key = key_value[0]
    value = key_value[1]

    function_name = f"get_{key}"
    function = getattr(configs_module, function_name)

    # Check raise error if key is not specified
    radar_api.config.set({key: None})
    with pytest.raises(ValueError):
        function()

    # Check returns the value specified in the donfig file
    radar_api.config.set({key: value})
    assert function() == value

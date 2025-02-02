<div align="center">

# Welcome to RADAR-API

![Radars currently accessible through RADAR-API](/docs/source/static/radar_api_coverage.png)

|                   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Deployment        | [![PyPI](https://badge.fury.io/py/radar_api.svg?style=flat)](https://pypi.org/project/radar_api/) [![Conda](https://img.shields.io/conda/vn/conda-forge/radar-api.svg?logo=conda-forge&logoColor=white&style=flat)](https://anaconda.org/conda-forge/radar-api)                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Activity          | [![PyPI Downloads](https://img.shields.io/pypi/dm/radar_api.svg?label=PyPI%20downloads&style=flat)](https://pypi.org/project/radar_api/) [![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/radar-api.svg?label=Conda%20downloads&style=flat)](https://anaconda.org/conda-forge/radar-api)                                                                                                                                                                                                                                                                                                                                                                                       |
| Python Versions   | [![Python Versions](https://img.shields.io/badge/Python-3.10%20%203.11%20%203.12%20%203.13-blue?style=flat)](https://www.python.org/downloads/)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Supported Systems | [![Linux](https://img.shields.io/github/actions/workflow/status/ghiggi/radar_api/.github/workflows/tests.yaml?label=Linux&style=flat)](https://github.com/ghiggi/radar_api/actions/workflows/tests.yaml) [![macOS](https://img.shields.io/github/actions/workflow/status/ghiggi/radar_api/.github/workflows/tests.yaml?label=macOS&style=flat)](https://github.com/ghiggi/radar_api/actions/workflows/tests.yaml) [![Windows](https://img.shields.io/github/actions/workflow/status/ghiggi/radar_api/.github/workflows/tests_windows.yaml?label=Windows&style=flat)](https://github.com/ghiggi/radar_api/actions/workflows/tests_windows.yaml)                                                |
| Project Status    | [![Project Status](https://www.repostatus.org/badges/latest/active.svg?style=flat)](https://www.repostatus.org/#active)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Build Status      | [![Tests](https://github.com/ghiggi/radar_api/actions/workflows/tests.yaml/badge.svg?style=flat)](https://github.com/ghiggi/radar_api/actions/workflows/tests.yaml) [![Lint](https://github.com/ghiggi/radar_api/actions/workflows/lint.yaml/badge.svg?style=flat)](https://github.com/ghiggi/radar_api/actions/workflows/lint.yaml) [![Docs](https://readthedocs.org/projects/radar_api/badge/?version=latest&style=flat)](https://radar-api.readthedocs.io/en/latest/)                                                                                                                                                                                                                      |
| Linting           | [![Black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat)](https://github.com/psf/black) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&style=flat)](https://github.com/astral-sh/ruff) [![Codespell](https://img.shields.io/badge/Codespell-enabled-brightgreen?style=flat)](https://github.com/codespell-project/codespell)                                                                                                                                                                                                                                                                 |
| Code Coverage     | [![Coveralls](https://coveralls.io/repos/github/ghiggi/radar_api/badge.svg?branch=main&style=flat)](https://coveralls.io/github/ghiggi/radar_api?branch=main) [![Codecov](https://codecov.io/gh/ghiggi/radar_api/branch/main/graph/badge.svg?token=G7IESZ02CW?style=flat)](https://codecov.io/gh/ghiggi/radar_api)                                                                                                                                                                                                                                                                                                                                                                            |
| Code Quality      | [![Codefactor](https://www.codefactor.io/repository/github/ghiggi/radar_api/badge?style=flat)](https://www.codefactor.io/repository/github/ghiggi/radar_api) [![Codebeat](https://codebeat.co/badges/57498d71-f042-473f-bb8e-9b45e50572d8?style=flat)](https://codebeat.co/projects/github-com-ghiggi-radar_api-main) [![Codacy](https://app.codacy.com/project/badge/Grade/bee842cb10004ad8bb9288256f2fc8af?style=flat)](https://app.codacy.com/gh/ghiggi/radar_api/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade) [![Codescene](https://codescene.io/projects/63299/status-badges/average-code-health?style=flat)](https://codescene.io/projects/63299) |
| License           | [![License](https://img.shields.io/github/license/ghiggi/radar_api?style=flat)](https://github.com/ghiggi/radar_api/blob/main/LICENSE)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Community         | [![Discourse](https://img.shields.io/badge/Slack-radar_api-green.svg?logo=slack&style=flat)](https://openradar.discourse.group/) [![GitHub Discussions](https://img.shields.io/badge/GitHub-Discussions-green?logo=github&style=flat)](https://github.com/ghiggi/radar_api/discussions)                                                                                                                                                                                                                                                                                                                                                                                                       |
| Citation          | [![DOI](https://zenodo.org/badge/922589509.svg?style=flat)](https://doi.org/10.5281/zenodo.14743651)                                                                                                                                                                                                                                                                                                                                                                                    </div>                                                                                                                                                                                                |

[**Documentation: https://radar-api.readthedocs.io**](https://radar-api.readthedocs.io/)

<div align="left">

## 🚀 Quick start

RADAR-API provides an easy-to-use python interface to find, download and
read weather radar data from several meteorological services.
Data are retrieved directly from cloud buckets.
Current radar networks supported are: NEXRAD, IDEAM and FMI.

The list of available radars can be retrieved using:

```python
import radar_api

radar_api.available_networks()
radar_api.available_radars()
radar_api.available_radars(network="NEXRAD")
```

Before starting using RADAR-API, we highly suggest to save into a configuration file
the directory on the local disk where to save the radar dataset of interest.

To facilitate the creation of the configuration file, you can run the following script:

```python
import radar_api

base_dir = (
    "<path/to/directory/RADAR"  # path to the directory where to download the data
)
radar_api.define_configs(base_dir=base_dir)

# You can check that the config file has been correctly created with:
configs = radar_api.read_configs()
print(configs)
```

______________________________________________________________________

### 📥 Download radar data

You can start to download radar data using the following code snippet:

```python
import radar_api

start_time = "2021-02-01 12:00:00"
end_time = "2021-02-01 13:00:00"

radar = "KABR"
network = "NEXRAD"

filepaths = radar_api.download_files(
    network=network,
    radar=radar,
    start_time=start_time,
    end_time=end_time,
)
```

______________________________________________________________________

### 💫 Open radar files into xarray or pyart

RADAR-API allows to read directly radar data from the cloud without the
need to previously download and save the files on your disk.

RADAR-API make use of pyart and xradar readers to open the files into either
an xarray object or pyart radar object.

```python
import radar_api
import pyart

# Search for files on cloud bucket
filepaths = radar_api.find_files(
    network=network,
    radar=radar,
    start_time=start_time,
    end_time=end_time,
    protocol="s3",
)
print(filepaths)
 
# Define the file to open
filepath = filepaths[0]

# Open all sweeps of a radar volume into a xradar datatree
dt = radar_api.open_datatree(filepath, network=network)

# Extract the radar sweep of interest
ds = dt["sweep_0"].to_dataset()

# Open directly a single radar sweep into a xradar dataset
ds = radar_api.open_dataset(filepath, network=network, sweep="sweep_0")

# Open all sweeps of a radar volume into a pyart radar object
radar_obj = radar_api.open_pyart(filepath, network=network)

# Display the data with pyart
display = pyart.graph.RadarDisplay(radar_obj)
display.plot("reflectivity")
display.set_limits((-150, 150), (-150, 150))
```

______________________________________________________________________

## 📖 Documentation

To discover RADAR-API utilities and functionalities,
please read the software documentation available at [https://radar-api.readthedocs.io/en/latest/](https://radar-api.readthedocs.io/en/latest/).

All RADAR-API tutorials are available as Jupyter Notebooks in the [`tutorial`](https://github.com/ghiggi/radar_api/tree/main/tutorials) directory.

______________________________________________________________________

## 🛠️ Installation

### conda

RADAR-API can be installed via [conda][conda_link] on Linux, Mac, and Windows.
Install the package by typing the following command in the terminal:

```bash
conda install radar-api
```

In case conda-forge is not set up for your system yet, see the easy to follow instructions on [conda-forge][conda_forge_link].

### pip

RADAR-API can be installed also via [pip][pip_link] on Linux, Mac, and Windows.
On Windows you can install [WinPython][winpy_link] to get Python and pip running.
Then, install the RADAR-API package by typing the following command in the terminal:

```bash
pip install radar-api
```

To install the latest development version via pip, see the [documentation][dev_install_link].

## 💭 Feedback and Contributing Guidelines

If you aim to contribute your data or discuss the future development of RADAR-API,
we suggest to join the [**Open Radar Science Discourse Group**](https://openradar.discourse.group/).

Feel free to also open a [GitHub Issue](https://github.com/ghiggi/radar_api/issues) or a [GitHub Discussion](https://github.com/ghiggi/radar_api/discussions) specific to your questions or ideas.

## Citation

If you are using RADAR-API in your publication please cite our Zenodo repository:

> Ghiggi Gionata. ghiggi/radar_api. Zenodo. [![<https://doi.org/10.5281/zenodo.14743651>](https://zenodo.org/badge/922589509.svg?style=flat)](https://doi.org/10.5281/zenodo.14743651)

If you want to cite a specific software version, have a look at the [Zenodo site](https://doi.org/10.5281/zenodo.14743651).

## License

The content of this repository is released under the terms of the [MIT license](LICENSE).

</div>

[conda_forge_link]: https://github.com/conda-forge/radar-api-feedstock#installing-radar-api
[conda_link]: https://docs.conda.io/en/latest/miniconda.html
[dev_install_link]: https://radar-api.readthedocs.io/en/latest/02_installation.html#installation-for-contributors
[pip_link]: https://pypi.org/project/radar-api
[winpy_link]: https://winpython.github.io/

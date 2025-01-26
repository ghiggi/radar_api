import radar_api
from radar_api.io import get_directory_pattern, get_network_filename_patterns

# List available networks and radars
radar_api.available_networks()
radar_api.available_radars()
radar_api.available_radars(network="NEXRAD")

# Define query settings
start_time = "2021-02-01 12:00:00"
end_time = "2021-02-01 13:00:00"
base_dir = None
fs_args = {}
verbose = True 

radar="KABR"
network = "NEXRAD"

#-------------------------------------------------------.
#### Download files 
filepaths = radar_api.download_files(
    network=network,
    radar=radar,
    start_time=start_time,
    end_time=end_time,
    fs_args=fs_args,
    progress_bar=True,
    check_data_integrity=True,
    force_download=False, 
    n_threads=10,
    verbose=verbose,
    )
print(filepaths)

#-------------------------------------------------------.
#### Search files 

# Search for files on cloud bucket 
filepaths = radar_api.find_files(
    network=network,
    radar=radar,
    start_time=start_time,
    end_time=end_time,
    fs_args=fs_args,
    protocol="s3",
    verbose=verbose,
    )
print(filepaths)

# Search for files locally 
filepaths = radar_api.find_files(
    network=network,
    radar=radar,
    start_time=start_time,
    end_time=end_time,
    fs_args=fs_args,
    protocol="local",
    verbose=verbose,
    )
print(filepaths)


# Group filepaths by key or time
dict_filepaths = radar_api.group_filepaths(filepaths, network=network, groups="volume_identifier")
dict_filepaths = radar_api.group_filepaths(filepaths, network=network, groups=["day","hour"])

# Get a single file
filepath = filepaths[0]

#-------------------------------------------------------.
#### Open files 

# Open xradar datatree
dt = radar_api.open_datatree(filepath, network=network)
dt = radar_api.open_datatree(filepath, network=network, chunks={})
dt["sweep_0"].to_dataset()

# Open xradar dataset (a single sweep)
ds = radar_api.open_dataset(filepath, network=network, group="sweep_0")

# Open pyart radar object
radar_obj = radar_api.open_pyart(filepath, network=network)

# Display data with pyart
import pyart
display = pyart.graph.RadarDisplay(radar_obj)
display.plot('reflectivity') # title="{} {}".format(scan.radar_id,scan.scan_time))
display.set_limits((-150, 150), (-150, 150))
 
#-------------------------------------------------------.
#### Search for radars available within a given time period 
radar_api.available_radars(network="FMI", start_time="2025-01-01", end_time=None)
radar_api.available_radars(network="FMI", end_time="2008-01-01")
 
radar_api.available_radars(network="SIDEAM", start_time="2025-01-01", end_time=None)
radar_api.available_radars(network="SIDEAM", end_time="2019-01-01")


radar_api.available_radars(network="NEXRAD", start_time="2025-01-01")
radar_api.available_radars(network="NEXRAD", end_time="1993-01-01")


#-------------------------------------------------------.
#### TODO Search for radars available at a given location

# available_radars_around_point(point, distance)

#-------------------------------------------------------.
# radar_api.available_radars(network=)
# radar = "fianj"
# network = "FMI"

  
 
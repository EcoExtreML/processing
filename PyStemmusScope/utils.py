import ast
import os
import re
from pathlib import Path
import numpy as np


def convert_to_lsm_coordinates(lat, lon):
    """Converts latitude in degrees North to NCAR's LSM coordinate system: Grid with lat
    values ranging from 0 -- 360, where 0 is the South Pole, and lon values ranging
    from 0 -- 720, where 0 is the prime meridian. Both representing a 0.5 degree
    resolution.

    Args:
        lat (float): Latitude in degrees North
        lon (float): longitude in degrees East

    Returns:
        (int, int): (nearest) latitude grid coordinates
    """
    lat += 90
    lat *= 2

    lon *= 2
    if lon < 0:
        lon += 720

    return np.round(lat).astype(int), np.round(lon).astype(int)


def os_name():
    return os.name


def to_absolute_path(
    input_path: str,
    parent: Path = None,
    must_be_in_parent=True,
) -> Path:
    """Parse input string as :py:class:`pathlib.Path` object.

    Args:
        input_path: Input string path that can be a relative or absolute path.
        parent: Optional parent path of the input path
        must_exist: Optional argument to check if the input path exists.
        must_be_in_parent: Optional argument to check if the input path is
            subpath of parent path

    Returns:
        The input path that is an absolute path and a :py:class:`pathlib.Path` object.
    """

    must_exist = False
    pathlike = Path(input_path)
    if parent:
        if not parent.is_absolute():
            # care for windows, see issue 22
            must_exist = os_name() == 'nt'
        pathlike = parent.joinpath(pathlike)
        if must_be_in_parent:
            try:
                pathlike.relative_to(parent)
            except ValueError as exc:
                raise ValueError(
                    f"Input path {input_path} is not a subpath of parent {parent}"
                ) from exc
    else:
        # care for windows, see issue 22
        must_exist = os_name() == 'nt'

    return pathlike.expanduser().resolve(strict=must_exist)

def get_forcing_file(config):
    """Get forcing file from the location.
    """
    location, fmt = check_location_fmt(config["Location"])
    # check if the forcing file exists for the given locaiton(s)
    # if fmt == "site":
    # elif fmt == "latlon"
    # elif fmt == "bbox"

def check_location_fmt(loc):
    """Check the format of location.

    Three types of format are supported:
    - Site name (e.g. "DE-Kli")
    - Latitude and longitude (e.g. "(56.4, 112.0)")
    - Bounding box (e.g. "(10,10), (10,20), (20,10), (20,20)")

    Args:
        loc: String of location extracted from config file.

    Returns:
        Location name (string) or location (tuple) lat,lon pair and its format
    """
    # remove all blanks
    loc = loc.replace(" ","")
    if re.fullmatch("[A-Z]{2}-[A-Z][a-z]{2}", loc):
        location = loc
        fmt = "site"
    elif re.fullmatch("\(\d*[.,]?\d*,\d*[.,]?\d*\)", loc):
        # turn string into tuples
        location = ast.literal_eval(loc)
        # check if the coordinate is valid
        check_lat_lon(location)
        fmt = "latlon"
    elif re.fullmatch("(\(\d*[.,]?\d*,\d*[.,]?\d*\)[,]?){4}", loc):
        # find items between brackets
        location = re.findall(r"\(.*?\)", loc)
        # turn string into tuples
        location = [ast.literal_eval(i) for i in location]
        for coordinates in location:
            check_lat_lon(coordinates)
        fmt = "bbox"
    else:
        raise ValueError(
            f"Location '{loc}' in the config file does not match expected format."
        )        
    
    return location, fmt

def check_time_fmt(start_time, end_time):
    """Check the format of time."""

def check_lat_lon(coordinates):
    """Check if the coordinates exists."""


import datetime as dt

import pandas as pd
import xarray as xr
import click
import sys
import os

from log import log, set_log_level_debug

DATA_DIRECTORY = "data"
CACHE_DIRECTORY = "forecasts"


@click.command("main", context_settings={"show_default": True})
@click.option(
    "--latitude",
    type=click.FloatRange(min=-90, max=90),
    default=52.371807,
    help="the latitude to fetch the forecast data for (default: Amsterdam)"
)
@click.option(
    "--longitude",
    type=click.FloatRange(min=0, max=359.75),
    default=4.896029,
    help="the longitude to fetch the forecast data for (default: Amsterdam)"
)
@click.option(
    "--datetime",
    type=click.DateTime(["%Y-%m-%d %H:00"]),
    default=str((dt.datetime.today() + dt.timedelta(days=1)
                 ).strftime("%Y-%m-%d 00:00")),  # Date today + 1 day
    help="the datetime in UTC to fetch the forecast data for, input should be in the future (default: tomorrow)"
)
@click.option(
    "--gfs-resolution",
    type=click.Choice(["0p25_1hr"]),
    default="0p25_1hr",
    help="the resolution to fetch the GFS forecast data for"
)
@click.option(
    "--stdout",
    type=click.BOOL,
    default=False,
    help="print the output result also to the console"
)
@click.option(
    "--debug",
    type=click.BOOL,
    default=False,
    help="sets the log level to debug (default: INFO)"
)
def main(latitude, longitude, datetime, gfs_resolution, stdout, debug):
    # Most of the input validation is handled by click, handle additional input below
    datetime_now = dt.datetime.now()
    if datetime < datetime_now:
        log.error(
            f"Given datetime should be in the future, given: {datetime}, now: {datetime_now}"
        )
        sys.exit(1)

    # Set logger level to DEBUG
    if debug:
        set_log_level_debug()

    get_gfs(latitude, longitude, datetime, gfs_resolution, stdout)


def get_gfs(
        latitude: float,
        longitude: float,
        requested_datetime: dt.datetime,
        gfs_resolution: str,
        stdout: bool
):
    # Get the GFS URL to read from and the GFS ID
    # The GFS ID
    # - Is used a filename for the output data and the cached files
    # - Identifies fully the forecast name that we read from
    gfs_url, gfs_id = get_gfs_url_and_id(requested_datetime, gfs_resolution)

    cached, cached_path = gfs_id_exists_in_cache(gfs_id)
    log.debug(f"gfs_url: {gfs_url}, gfs_id: {gfs_id} (cached: {cached})")

    # Read from the local or the remote
    if not cached:
        read_path = gfs_url
    else:
        read_path = cached_path

    log.debug(f"Reading from: {read_path}")
    with xr.open_dataset(read_path) as ds:
        if not cached:
            log.debug(f"Caching gfs_id: {gfs_id}")
            # TODO: Implement me *ds.to_netcdf()*

        # Filter the data and write the output
        data = filter_dataset(ds, latitude, longitude, requested_datetime)
        df = data.to_dataframe()
        write_df_to_csv(df, DATA_DIRECTORY, gfs_id)

        # Send the filtered data to STDOUT
        if stdout:
            print(df)


def get_gfs_url_and_id(
        datetime: dt.datetime,
        gfs_resolution: str
):
    # Example: https://nomads.ncep.noaa.gov/dods/gfs_0p25_1hr/gfs20231015/gfs_0p25_1hr_00z.dds
    # Latest forecast is on today's date
    gfs_date_today = dt.datetime.today().strftime("%Y%m%d")

    # Get the GFS corresponding run to search the data of
    gfs_run = get_gfs_run_from_datetime(datetime)
    gfs_filepath = f"gfs{gfs_date_today}/gfs_{gfs_resolution}_{gfs_run}"
    gfs_id = gfs_filepath.replace("/", "_")

    return f"https://nomads.ncep.noaa.gov/dods/gfs_{gfs_resolution}/{gfs_filepath}", gfs_id


def create_directory(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)


def write_df_to_csv(
        df: pd.DataFrame,
        directory: str,
        gfs_id: str
):
    create_directory(directory)
    path = f"{directory}/{gfs_id}.csv"

    # If file exists already we don't need to add the CSV header
    add_header = True
    if os.path.exists(path):
        add_header = False

    log.debug(f"Writing dataframe to: {path}, with header: {add_header}")
    df.to_csv(
        path,
        sep=',',
        encoding='utf-8',
        mode='a',
        header=add_header
    )


def filter_dataset(
        dataset: xr.Dataset,
        latitude: float,
        longitude: float,
        datetime: dt.datetime
):
    # Interpolate the data for the region and time we are interested in
    # Variables are defined here: https://nomads.ncep.noaa.gov/dods/gfs_0p25_1hr/gfs20231014/gfs_0p25_1hr_00z.das
    return dataset[["tmpsfc"]].interp(lon=longitude, lat=latitude).sel(
        time=slice(datetime, datetime)
    )


def gfs_id_exists_in_cache(gfs_id: str):
    path = f"{CACHE_DIRECTORY}/{gfs_id}.csv"
    if os.path.exists(path):
        return True, path
    return False, ""


def get_gfs_run_from_datetime(datetime: dt.datetime):
    # Could be that the latest run won't contain the requested datetime as
    # each run has predictions from the specified time dimension. For example,
    # 18z has predictions from 18:00:00, 19:00:00 and so on. Below we pick the most
    # recent/latest run that fulfils the datetime requested if necessary
    now = dt.datetime.now()
    time06 = now.replace(hour=6, minute=0, second=0, microsecond=0)
    time12 = now.replace(hour=12, minute=0, second=0, microsecond=0)
    time18 = now.replace(hour=18, minute=0, second=0, microsecond=0)

    # Available runs based on the data are on 00z, 06z, 12z, 18z
    # See: https://nomads.ncep.noaa.gov/dods/gfs_0p25_1hr/gfs20231015
    # Pick always the latest run
    run = "18z"

    if datetime.time() < time18.time():
        run = "12z"
        if datetime.time() < time12.time():
            run = "06z"
            if datetime.time() < time06.time():
                run = "00z"

    return run


if __name__ == '__main__':
    main()

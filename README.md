# GFS Forecast of temperature

A Python CLI application that fetches the GFS forecast data from https://nomads.ncep.noaa.gov/. The application leverages
OpenDAP to access the data since it provides a way to filter them using expressions. You can read more information about
OpenDAP and the key terms [here](https://www.earthdata.nasa.gov/engage/open-data-services-and-software/api/opendap).

As for the forecast model, the application uses the GFS 0.25 degree on an hourly basis for high precision data. By degree
is meant that the analysis happens by 0.25 global latitude longitude grid; earth is divided into coordinate-spaced grids.
The lower the degree, the higher the precision of the forecast. As far as the "hourly" choice is concerned, it has been
selected for precision reasons, but also to provide the ability to search the data on a specific point in time.

To manipulate the multidimensional data coming from OpenDAP, the application uses [Xarray](https://github.com/pydata/xarray)
which is a very popular library for this purpose.


## Prerequisites
Verify you have the Python runtime installed on your machine. These days you want to stick with Python 3.
If you're on macOS or on any GNU/Linux distribution, chances are you already have it installed.

```bash
$ python -V
Python 3.9
```

If you don't have the Python runtime already installed on your machine, you can install it via the
official Python installer (https://www.python.org/downloads/) or use an OS-specific package management system,
e.g. using `brew` for macOS or `apt` on a Debian/Ubuntu GNU/Linux distribution.

- Create a Python virtual environment and activate it.
```bash
$ python -m venv ve
$ source ve/bin/activate
```

**NOTE**: once you activate the virtual environment, the shell prompt will automatically reflect it. The virtual
environment is only active within the context of the current shell. If you open a different shell, you'll need to
reactivate it.

Virtual environments are *very* common in Python. You can learn more about them here: https://docs.python.org/3/library/venv.html

- Install the requirements into the virtual environment.
```bash
(ve) $ pip install -r requirements.txt
```


### How to run?

The CLI application accepts a number of command-line arguments leveraging [click](https://click.palletsprojects.com/en/8.1.x/). Click allows us to generate beautiful
and validated command-line interfaces in a composable way with as little code as necessary. There are default values for
all the inputs required, thus, you can simply execute the application by running:
```bash
(ve) $ python ./app/main.py
```

The output will be a CSV file. By default, the script requests the temperature for `Amsterdam`,
for tomorrow (current date plus 1 day) and time is set to 00:00.

If you wish to pass custom command-line arguments you can do so as per the example below:
```bash
(ve) $ python ./app/main.py --latitude=4.896029 --longitude=52.371807 --datetime="2023-10-26 12:00"
```

The application has a number of constraints when it comes to the input accepted, but also accepts other type of input.
For a complete overview, you can run:
```bash
(ve) $ python ./app/main.py --help
```

#### Using Docker

You can run the application also through Docker. For that, a `Dockerfile` is provided at the rood directory. To build
the Docker container you can leverage the Makefile. The following command will build a Docker image with the name `gfs-fetch`:

```bash
$ make docker-build
```

By default, the Docker container writes the output also to the console. In order to run the container, trigger the
following command which will run the application with the default command-line arguments:
```bash
$ make docker-run
```

If you wish to modify the command-line arguments when running the Docker image, you can either modify the `docker-run`
entry in the Makefile or manually run the Docker image:
```bash
$ docker run gfs-fetch python /app/main.py --latitude=4.896029 --longitute=52.371807 --datetime=2023-10-26 12:00
```


### Pre-commit

This project uses pre-commit(https://pre-commit.com/) to integrate code checks used to gate commits.

**NOTE**: When pushing to GitHub, an action runs these same checks. Using `pre-commit` locally ensures these checks will not fail.

```bash
# required only once
$ pre-commit install
pre-commit installed at .git/hooks/pre-commit

# run checks on all files
$ make pre-commit
```


### Other management tasks

The application comes with a handy Makefile to handle management tasks. For more information on the available targets,
you can access the inline help.

```bash
$ make help
```


## Assumptions

- Require a combination of date/time as input
- Date given is always in the future
- Time is always in UTC and only hours are accepted due to hourly forecast
- We are interested only in the surface temperature
- The temperature is in Kelvin, a conversion to Celsius can be a possible transformation afterward.
- All the files exist in the remote server always

## Open Issues

- Implement testing
- Exception handling if files do not exist. There could be an issue when determining the run of GFS to fetch the data for.
There can be cases where the server did not upload the data yet, thus, the application will fail.
- Fix warning of serialization warning of Xarray
```
SerializationWarning: Ambiguous reference date string: 1-1-1 00:00:0.0. The first value is assumed to be the year hence will
be padded with zeros to remove the ambiguity (the padded reference date string is: 0001-1-1 00:00:0.0). To remove this message,
remove the ambiguity by padding your reference date strings with zeros.
```
- Caching: there was an issue with storing the file in the local storage. Possibly a timeout or rate limiting on the server side.
```
oc_open: server error retrieving url: code=? message="Error {
    code = 0;
    message = "subset operation failed; process exceeded time limit of 100 sec";
}"2023-10-25:19:41:25 DEBUG    [common.py:161] getitem failed, waiting 958 ms before trying again (6 tries remaining). Full traceback: Traceback (most recent call last):
  File "src/netCDF4/_netCDF4.pyx", line 4958, in netCDF4._netCDF4.Variable.__getitem__
  File "src/netCDF4/_netCDF4.pyx", line 5916, in netCDF4._netCDF4.Variable._get
  File "src/netCDF4/_netCDF4.pyx", line 2029, in netCDF4._netCDF4._ensure_nc_success
RuntimeError: NetCDF: file not found
```

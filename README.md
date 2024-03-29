# Weather Anomaly Data (Micro)Service (WADS)

Data service backend for Weather Anomaly tool.

# DEPRECATED

This service has been rolled into the [Station Data Portal Backend](https://github.com/pacificclimate/station-data-portal-backend). This project is no longer maintained and will be deleted soon.

<strike>
 
## Summary

This microservice provides data useful for inspecting weather anomalies. 
Its primary client is the Weather Anomaly Tool.

Specifically, it provides:

* Baseline data: Multi-year averages of:
  * Monthly average of daily maximum temperature (tmax)
  * Monthly average of daily minimum temperature (tmin)
  * Monthly total precipitation (precip)
* Weather data: For a given year and month:
  * Monthly average of daily maximum temperature (tmax)
  * Monthly average of daily minimum temperature (tmin)
  * Monthly total precipitation (precip)

Each endpoint returns a list containing one data object per station, for all stations in the database. No filtering
on station (by location or any other crieria) is available at this time.

Each data object contains station information (including network, station native id, and location) and the data
at that station as appropriate to the endpoint (e.g., baseline monthly average of daily maxmimum temperature for
a specified month).

## Endpoints

We follow RESTful conventions in this microservice. Specifically:

* Each dataset is regarded as a resource. 
  (In this case, the resources are read-only, hence only the GET verb is allowed on them.)
* Resources are named (URI) hierarchically, where real hierarchy exists.
* Where there is no hierarchy, but there are several components to a hierarchical level, those components stay in the
  path and are separated by appropriate punctuation such as semicolon or comma (we use semicolon). 
  * In our case, this is the combination of variable and year/month specifiers.
  * This is not a universal convention; many APIs put such specifiers in query parameters.
  * See [this stackoverflow discussion](http://stackoverflow.com/a/31261026)
  and [this one](http://stackoverflow.com/a/11569077)
* Resources are named such that optional specifiers and filtering, ordering, 
  and other algorithmic specifiers (parameters) are in query parameters.
  * We have no such specifiers (yet: we may add filtering on station location, etc.)

Therefore we have the following resource URIs:

* Baseline data: `/baseline/<variable>;<month>`
* Weather data: `/weather/<variable>;<year>-<month>`

where

* `<variable>` is `'tmax'`, `'tmin'`, or `'precip'`
* `<year>` is an integer between 1850 and 2100, specifying the year of interest
* `<month>` is an integer between 1 and 12, specifying the month of interest

(Note: We could use Swagger (http://swagger.io/) for this sepcification!)

## Responses

### General

Endpoints return results as JSON (application/json). 

Success is indicated by a 200 OK status.

Any invalid URI results in a 404 Not Found status. Specifically,
invalid values for `<variable>`, `<year>`, or `<month>` result in a 404 Not Found.

### `/baseline/<variable>;<month>` endpoints

Response data on success (200):

```json
[
    {
        "network_name": String,
        "station_native_id": String,
        "station_name": String,
        "lon": Number,
        "lat": Number,
        "elevation": Number,
        "datum": Number
    },
    ...
]
```

`"datum"` is the value of the requested climate variable for the station.

For weather data, `<requested info>` is two dictionary items, one containing the value of the 
requested aggregate weather variable, and the other a number between 0 and 1 indicating the fraction of 
actual observations contributing to the aggregate value relative to the possible number of observations contributing:


### `/weather/<variable>;<year>-<month>` endpoints

Response data on success (200):

```json
[
    {
        "network_name": String,
        "station_native_id": String,
        "station_name": String,
        "lon": Number,
        "lat": Number,
        "elevation": Number,
        "frequency": String,
        "network_variable_name": String,
        "statistic": Number,
        "data_coverage": Number
    },
    ...
]
```

`"statistic"` is the value of the requested aggregate weather variable at the station

`"data_coverage"` is a fraction in range [0,1] of count of actual observations to possible observations
in month for aggregate (depends on frequency of observation of specific variable)

## Requirements

```
libpq-dev 
python-dev
postgresql-client
```

## Installation

It is best practice to install using a virtual environment.
Current recommended practice for Python3.3+ to use the [builtin `venv` module](https://docs.python.org/3/library/venv.html).
(Alternatively, `virtualenv` can still be used but it has shortcomings corrected in `venv`.)
See [Creating Virtual Environments](https://packaging.python.org/installing/#creating-virtual-environments) for an
overview of these tools.

```bash
$ git clone https://github.com/pacificclimate/weather-anomaly-data-service
$ cd weather-anomaly-data-service
$ python3 -m venv venv
$ source venv/bin/activate
(venv)$ pip install -U pip --user
(venv)$ pip install -i https://pypi.pacificclimate.org/simple/ -e .
(venv)$ pip install -r test_requirements.txt
```

### Configuration

Database dsn can be configured with the `PCDS_DSN` environment variable. 
Defaults to `postgresql://httpd@monsoon.pcic.uvic.ca/crmp`

```bash
(venv)$ PCDS_DSN=postgresql://dbuser:dbpass@dbhost/dbname scripts/devserver.py -p <port>
```

### Testing

#### Within the virtual environment:

(Make sure you have installed the packages in `test_requirements.txt` as instructed above.)

```bash
py.test -v
```

### Using Docker

#### Building images

To build production image:

```bash
docker build -t pcic/weather-anomaly-data-service . 
```

To build development/testing image:

```bash
docker build -t pcic/weather-anomaly-data-service-dev  -f Dockerfile.dev .
```

To run tests (note: must use dev/test image):

```bash
docker run --rm -it -v $(pwd):/app --name wads-test pcic/weather-anomaly-data-service-dev bash -c "su -m user -c 'py.test -v tests'"
```

## Misc

Change to trigger DockerHub automated build ...

</strike>

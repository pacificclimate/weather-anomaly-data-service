# weather-anomaly-data-service
Data service backend for Weather Anomaly tool.
=======
# Weather Anomaly Data (Micro)Service (WADS)

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
* The resources are read-only, hence only the GET verb is allowed on them.
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

* Baseline data: `<base URL>/baseline/<variable>;<month>`
* Weather data: `<base URL>/weather/<variable>;<year>-<month>`

where

* `<variable>` is `'tmax'`, `'tmin'`, or `'precip'`
* `<year>` is an integer between 1850 and 2100, specifying the year of interest
* `<month>` is an integer between 1 and 12, specifying the month of interest

(Note: We could use Swagger (http://swagger.io/) for this!)

### Success responses

Success is indicated by a 200 OK status.

Endpoints return results as JSON (application/json). Nominal JSON spec:
```json
[
    {
        "network_name": String,
        "native_id": String,
        "station_name": String,
        "lon": Number,
        "lat": Number,
        "elevation": Number,
        <requested datum>
    },
    ...
]
```

### Failure responses

Any invalid URI results in a 404 Not Found status. Specifically,
invalid values for `<variable>`, `<year>`, or `<month>` result in a 404 Not Found.

## Requirements

libpq-dev(???) python-dev

## Installation

It is best practice to install using `virtualenv`.

```bash
$ git clone https://github.com/pacificclimate/weather_anomaly_service
$ cd weather_anomaly_service
$ virtualenv venv
$ source venv/bin/activate
(venv)$ pip install -U pip
(venv)$ pip install -i http://pypi.pacificclimate.org/simple/ -e .
```

### Configuration

Database dsn can be configured with the `CRMP_DSN` environment variable. 
Defaults to `??? TBD`

```bash
(venv)$ CRMP_DSN=postgresql://dbuser:dbpass@dbhost/dbname scripts/devserver.py -p <port>
```

### Testing

#### Within the virtual environment:

```bash
pip install pytest
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
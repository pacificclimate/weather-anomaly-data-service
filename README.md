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
* Weather data:
  * Monthly average of daily maximum temperature (tmax)
  * Monthly average of daily minimum temperature (tmin)
  * Monthly total precipitation (precip)

## Endpoints

We could use Swagger (http://swagger.io/) for this!

* Baseline data: `<base URL>/baseline/<variable>;<month>`
* Weather data: `<base URL>/weather/<variable>;<year>-<month>`

where

* `<variable>` is `'tmax'`, `'tmin'`, or `'precip'`
* `<year>` is an integer between 1850 and 2100, specifying the year of interest
* `<month>` is an integer between 1 and 12, specifying the month of interest

Endpoints return results as JSON (application/json).

Invalid values for `<variable>`, `<year>`, or `<month>` result in a 404 Not Found.

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
(venv)$ pip install --trusted-host tools.pacificclimate.org -i http://tools.pacificclimate.org/pypiserver/ -e .
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

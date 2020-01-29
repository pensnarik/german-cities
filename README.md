![Cities count](https://img.shields.io/badge/cities-2052-green)

# Cities of Germany

This repository contains information about 2056 cities of Germany in JSON format and
Python script which is used to keep this up to date.

JSON format is the following.

Field|Description
----|--------
name|City name
state|State
district|District
population|City population
coords|Coordinates ('lat' - latitude, 'lon' - longtitude)
area|City area (in sq. km)

Data in JSON file are sorted by city name alphabetically.

All data are taken from [Wikipedia](https://en.m.wikipedia.org/wiki/List_of_cities_and_towns_in_Germany). The
script uses `parselab` Python package from [homonymous project](https://github.com/pensnarik/parselab) for
file caching and to abstract the complexities of network interaction.

This data is released for use under a [Creative Commons](https://creativecommons.org) license.

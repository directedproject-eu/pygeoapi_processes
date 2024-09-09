# DIRECTED pyGeoAPI Processes

## Build preparations

Download the file `dnk_ppp_2020_1km_Aggregated_UNadj.tif` from the [Nextcloud](https://cloud.tu-braunschweig.de/apps/files/?dir=/directed_shared/work_packages/wp2_interoperability/DATA/Exposures&fileid=569409494) and store it in `./data`.

## Build the Docker image

```console
docker compose build
```

## Start the Docker container

```console
docker compose up -d && docker compose logs -f
```

pygeoapi is running at <http://localhost:5000>

## Execute a process

```console
curl -X POST -H "Content-Type: application/json" -d "{\"inputs\":{\"intensity\": [0, 30, 80]}}" http://localhost:5000/processes/climada-simple-example-denmark-process/execution > out.csv
```

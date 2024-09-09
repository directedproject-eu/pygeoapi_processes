FROM geopython/pygeoapi:latest

#
#   install latest system updates
#
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Install custom processes
RUN mkdir -p /pygeoapi/data/processes
COPY ./data/dnk_ppp_2020_1km_Aggregated_UNadj.tif /pygeoapi/data/processes/dnk_ppp_2020_1km_Aggregated_UNadj.tif
COPY ./src /directed_pygeoapi_processes/src
COPY ./requirements.txt /directed_pygeoapi_processes/requirements.txt
COPY ./pyproject.toml /directed_pygeoapi_processes/pyproject.toml
RUN cd /directed_pygeoapi_processes && pip install .

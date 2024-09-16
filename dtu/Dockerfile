FROM ubuntu:jammy

ARG DEBIAN_FRONTEND=noninteractive

#
#   install latest system updates and additional system libraries
#
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install --assume-yes --no-install-recommends \
        gnupg \
        software-properties-common \
        wget \
    && rm -rf /var/lib/apt/lists/*

#
#   add qgis signing key
#
RUN echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/qgis-archive-keyring.gpg] https://qgis.org/debian jammy main" >> /etc/apt/sources.list.d/qgis.list \
    && wget --quiet -O /etc/apt/keyrings/qgis-archive-keyring.gpg https://download.qgis.org/downloads/qgis-archive-keyring.gpg

#
#   install qgis
#
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install --assume-yes --no-install-recommends  \
        qgis \
        python3-qgis \
    && rm -rf /var/lib/apt/lists/*

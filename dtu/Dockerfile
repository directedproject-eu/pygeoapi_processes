FROM ubuntu:jammy

ARG DEBIAN_FRONTEND=noninteractive
ARG URL_OS2DAMAGECOST=https://github.com/Skadesokonomi/Installation/raw/refs/heads/main/OS2DamageCost.zip
ARG URL_OS2DAMAGECOSTADMIN=https://github.com/Skadesokonomi/Installation/raw/refs/heads/main/OS2DamageCostAdmin.zip

#
#   install latest system updates and additional system libraries
#
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install --assume-yes --no-install-recommends \
        gnupg \
        software-properties-common \
        unzip \
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

#
#   install DTU cost damage model qgis plugin
#
WORKDIR /usr/share/qgis/python/plugins
# filter exit code 1 for unzip as unzip sets it to 1 for warnings
RUN wget --quiet -O OS2DamageCost.zip $URL_OS2DAMAGECOST \
    && unzip -q OS2DamageCost.zip | ( if [ $? == 1 ]; then exit 0; fi ) \
    && rm OS2DamageCost.zip \
    && wget --quiet -O OS2DamageCostAdmin.zip $URL_OS2DAMAGECOSTADMIN \
    && unzip -q OS2DamageCostAdmin.zip | ( if [ $? == 1 ]; then exit 0; fi ) \
    && rm OS2DamageCostAdmin.zip

COPY entrypoint.sh /home/entrypoint.sh
COPY init_dtu_model.py /home/init_dtu_model.py

WORKDIR /home

ENTRYPOINT /bin/sh /home/entrypoint.sh && /bin/sh
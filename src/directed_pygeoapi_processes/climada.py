# =================================================================
#
# Authors: Martin Pontius <m.pontius@52north.org>
#          Chahan Kropf
#          Victor Wattin Håkansson
#
# Copyright (c) 2024 52°North Spatial Information Research GmbH
# Copyright (c) 2024 Chahan Kropf
# Copyright (c) 2024 Victor Wattin Håkansson
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

import logging
import os
import uuid

from climada.engine import ImpactCalc
from climada.entity import Exposures, ImpactFunc, ImpactFuncSet
from climada.util.api_client import Client
from pygeoapi.process.base import BaseProcessor, ProcessorExecuteError


LOGGER = logging.getLogger(__name__)


SUPPORTED_HAZARD_TYPES = ["river_flood", "tropical_cyclone", "storm_europe", "relative_cropyield", "wildfire",
                          "earthquake", "flood", "hail", "aqueduct_coastal_flood"],
SUPPORTED_CLIMATE_SCENARIOS = ['None', 'ssp585', 'ssp245', 'ssp370', 'ssp126']
SUPPORTED_DATA_SOURCES = ['WISC', 'CMIP6', 'ERA5']
# GCM = General Circulation Model?, Global Climate Model?
SUPPORTED_GCMS = ['CMCC-CM2-SR5', 'HadGEM3-GC31-LL', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'MPI-ESM1-2-HR', 'MIROC6', 'CanESM5',
                  'GFDL-CM4', 'UKESM1-0-LL', 'GISS-E2-1-G', 'INM-CM5-0', 'CNRM-ESM2-1', 'CNRM-CM6-1', 'ACCESS-CM2',
                  'MIROC-ES2L', 'INM-CM4-8', 'MRI-ESM2-0', 'IPSL-CM6A-LR', 'MPI-ESM1-2-LR', 'EC-Earth3-CC', 'FGOALS-g3',
                  'EC-Earth3', 'EC-Earth3-Veg-LR', 'AWI-CM-1-1-MR', 'CNRM-CM6-1-HR', 'KACE-1-0-G', 'BCC-CSM2-MR',
                  'EC-Earth3-Veg', 'NESM3', 'HadGEM3-GC31-MM']
SUPPORTED_EXPOSURE_TYPES = ["litpop", "crop_production", "ssp_population", "crops"]

# Process metadata and description
PROCESS_METADATA = {
    'version': '0.1.0',
    'id': 'climada-simple-example-denmark',
    'title': {
        'en': 'CLIMADA simple example for Denmark'
    },
    'description': {
        'en': 'A simple example process on how to use CLIMADA in Denmark to calculate the impact of storm events.'
    },
    'jobControlOptions': ['sync-execute', 'async-execute'],
    'outputTransmission': ['value', 'reference'],
    'keywords': ['directed', 'climada', 'simple example'],
    'links': [{
        'type': 'text/html',
        'rel': 'about',
        'title': 'information',
        'href': 'https://github.com/CLIMADA-project/climada_python',
        'hreflang': 'en-US'
    }],
    'inputs': {
        'intensity': {
            'title': 'intensity',
            'description': 'mandatory; the intensity steps used for defining the impact function',
            'schema': {
                'type': 'array'
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['intensity']
        },
        'climate_scenario': {
            'title': 'climate_scenario',
            'description': 'optional; climate scenario',
            'schema': {
                'type': 'string'
            },
            'minOccurs': 0,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['climate_scenario']
        },
        'data_source': {
            'title': 'data_source',
            'description': 'optional; data source',
            'schema': {
                'type': 'string'
            },
            'minOccurs': 0,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['data_source']
        },
        'gcm': {
            'title': 'GCM',
            'description': 'optional; Global Climate Model (GCM) to use',
            'schema': {
                'type': 'string'
            },
            'minOccurs': 0,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['gcm']
        },
        'mdd': {
            'title': 'mdd',
            'description': 'optional; mean damage (impact) degree',
            'schema': {
                'type': 'array'
            },
            'minOccurs': 0,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['mdd']
        },
        'paa': {
            'title': 'paa',
            'description': 'optional; percentage of affected assets (exposures)',
            'schema': {
                'type': 'array'
            },
            'minOccurs': 0,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['paa']
        },
        'nearest_neighbor_threshold': {
            'title': 'nearest_neighbor_threshold',
            'description': 'optional; nearest neighbor threshold',
            'schema': {
                'type': 'number'
            },
            'minOccurs': 0,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['nearest_neighbor_threshold']
        },
        'return_periods': {
            'title': 'return_periods',
            'description': 'optional; return periods',
            'schema': {
                'type': 'array'
            },
            'minOccurs': 0,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['return_periods']
        }
    },
    'outputs': {
        'impact': {
            'title': 'impact',
            'description': 'Calculated impact',
            'schema': {
                'type': 'object',
                'contentMediaType': 'text/csv'
            }
        }
    },
    'example': {
        'inputs': {
            'intensity': [0, 30, 80]
        }
    }
}


class SimpleExampleDenmarkProcessor(BaseProcessor):
    """Simple Example Processor for CLIMADA"""

    def __init__(self, processor_def):
        """
        Initialize object
        :param processor_def: provider definition
        :returns: pygeoapi.process.hello_world.SimpleExampleProcessor
        """
        LOGGER.debug("Initialize SimpleExampleDenmarkProcessor.")
        super().__init__(processor_def, PROCESS_METADATA)


    def execute(self, data, outputs=None):
        LOGGER.info("Execute SimpleExampleDenmarkProcessor.")
        LOGGER.info(f"outputs: {outputs}")
        # ----------- #
        # Parse input #
        # ----------- #
        intensity = data.get('intensity')
        climate_scenario = data.get('climate_scenario', 'ssp585')
        data_source = data.get('data_source', 'CMIP6')
        gcm = data.get('gcm', 'CMCC-ESM2')
        mdd = data.get('mdd', (0, 1))
        paa = data.get('paa', (1, 1))
        # threshold for nearest neighbour assignment is chosen to 1.5 km as the population dataset is a 1 km resolution
        # (arbitrary choice, default would be 100)
        nearest_neighbor_threshold = data.get('nearest_neighbor_threshold', 1.5)  # km
        return_periods = data.get('return_periods', [1, 2, 5, 10, 20])

        if intensity is None:
            raise ProcessorExecuteError('Cannot process without an intensity')
        if len(intensity) != 3:
            raise ProcessorExecuteError(f'The intensity tuple must have three elements, {len(intensity)} found')
        if climate_scenario not in SUPPORTED_CLIMATE_SCENARIOS:
            raise ProcessorExecuteError(f'The climate_scenario {climate_scenario} is not supported. Supported climate '
                                        f'scenarios: {SUPPORTED_CLIMATE_SCENARIOS}')
        if data_source not in SUPPORTED_DATA_SOURCES:
            raise ProcessorExecuteError(f'The data_source {data_source} is not supported. Supported data sources: '
                                        f'{SUPPORTED_DATA_SOURCES}')
        if gcm not in SUPPORTED_GCMS:
            raise ProcessorExecuteError(f'The gcm {gcm} is not supported. Supported gcms: {SUPPORTED_GCMS}')
        if len(mdd) != 2:
            raise ProcessorExecuteError(f'The mdd tuple must have two elements, {len(mdd)} found')
        if len(paa) != 2:
            raise ProcessorExecuteError(f'The paa tuple must have two elements, {len(paa)} found')

        LOGGER.debug(f"""
        --------
        Settings
        --------
        {'intensity':>26} = {str(intensity)}
        {'climate_scenario':>26} = {climate_scenario}
        {'data_source':>26} = {data_source}
        {'gcm':>26} = {str(gcm)}
        {'mdd':>26} = {str(mdd)}
        {'paa':>26} = {str(paa)}
        {'nearest_neighbor_threshold':>26} = {nearest_neighbor_threshold}
        {'return_periods':>26} = {str(return_periods)}
        """)

        client = Client()

        # ------ #
        # Hazard #
        # ------ #
        haz = client.get_hazard(
            hazard_type='storm_europe',
            properties={
                'climate_scenario': climate_scenario,
                'spatial_coverage': 'Europe',
                'data_source': data_source,
                'gcm': gcm
            }
        )

        # -------- #
        # Exposure #
        # -------- #
        # Worldpop population distribution for Denmark
        exp_file = '/pygeoapi/data/processes/dnk_ppp_2020_1km_Aggregated_UNadj.tif'
        exp = Exposures.from_raster(exp_file)

        # --------------- #
        # Impact function #
        # --------------- #
        impf_id1 = 1
        impf1 = ImpactFunc.from_step_impf(
            intensity=intensity,
            mdd=mdd,
            paa=paa,
            haz_type=haz.haz_type,
            impf_id=impf_id1
        )
        impfset = ImpactFuncSet([impf1])
        exp.gdf[f'impf_{haz.haz_type}'] = impf_id1
        exp.assign_centroids(haz, threshold=nearest_neighbor_threshold)

        # ------------------ #
        # Impact calculation #
        # ------------------ #
        impcalc = ImpactCalc(exposures=exp, impfset=impfset, hazard=haz)
        impact = impcalc.impact(assign_centroids=False)
        # Impact at given return periods
        impact.calc_freq_curve(return_per=return_periods)
        # Save to csv
        # FIXME: don't save the file to disk, but use only an in-memory file
        out_file = f'/tmp/impact_simple_example_wind_denmark_{str(uuid.uuid4())}.csv'
        impact.write_csv(out_file)

        # ------ #
        # Output #
        # ------ #
        with open(out_file, mode='rb') as f:
            csv = f.read()
        # pygeoapi saves the output by itself, so we are deleting the temporary file
        try:
            os.remove(out_file)
        except FileNotFoundError:
            LOGGER.warning(f"Could not delete the temporary file {out_file}")
        mimetype = 'text/csv'
        # mimetype = 'application/json'
        # outputs = {
        #     'id': 'impact',
        #     'value': out_file
        # }
        return mimetype, csv

    def __repr__(self):
        return f'<SimpleExampleDenmarkProcessor> {self.name}'

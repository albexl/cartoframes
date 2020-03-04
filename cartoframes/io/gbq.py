"""Functions to interact with the Google BigQuery platform"""

import os
import json
import time

from .managers.gbq_manager import GBQManager
from ..viz.sources import GeoDataFrameSource, GBQTilesetSource
from ..utils.utils import is_sql_query
from ..utils.logger import log


def get_project():
    return os.environ.get('GOOGLE_CLOUD_PROJECT')


def get_token():
    path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if path:
        with open(path) as f:
            adc = json.load(f)
            if adc:
                resp = adc.get('token_response')
                if resp:
                    return resp.get('access_token')


def create_tileset(data, name=None, project=None, credentials=None, index_col='geoid', geom_col='geom'):
    raise NotImplementedError()


def prepare_gbq_source(data, project=None, token=None, force_df=False, force_mvt=False):
    if not isinstance(data, str):
        raise ValueError('Wrong source input. Valid values are str.')

    query = _get_gbq_query(data)
    manager = GBQManager(project, token)

    if not force_mvt and (force_df or manager.estimated_data_size(query) < manager.DATA_SIZE_LIMIT):
        log.info('Downloading data. This may take a few seconds')

        begin = time.time()

        df = manager.download_dataframe(query)

        end = time.time()

        print('DEBUG: time elapsed {:.2f}s'.format(end - begin))

        return GeoDataFrameSource(df, geom_col='geom')
    else:
        log.info('Preparing data. This may take a few minutes')

        begin = time.time()

        data = manager.fetch_mvt_data(query)
        metadata = manager.fetch_mvt_metadata(query)
        bounds, zoom = manager.compute_bounds(query)
        manager.trigger_mvt_generation(query, zoom)

        end = time.time()

        print('DEBUG: time elapsed {:.2f}s'.format(end - begin))

        return GBQTilesetSource(data, metadata, bounds, zoom)


def _get_gbq_query(source):
    return source if is_sql_query(source) else 'SELECT * FROM `{}`'.format(source)

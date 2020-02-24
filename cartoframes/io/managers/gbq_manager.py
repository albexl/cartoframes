import os

from google.cloud import bigquery
from google.oauth2.credentials import Credentials

from ...utils.logger import log
from ...utils.utils import dtypes2vl, create_hash

GEOID_KEY = 'geoid'
GEOM_KEY = 'geom'
MVT_DATASET = 'mvt_pool'
PROJECT_KEY = 'GOOGLE_CLOUD_PROJECT'


class GBQManager:

    DATA_SIZE_LIMIT = 10 * 1024 * 1024  # 10 MB

    def __init__(self, project=None, token=None):
        credentials = Credentials(token) if token else None

        self.token = token
        self.project = project if project else os.environ[PROJECT_KEY]
        self.client = bigquery.Client(project=project, credentials=credentials)

    def download_dataframe(self, query):
        query_job = self.client.query(query)
        return query_job.to_dataframe()

    def fetch_mvt_data(self, query):
        return {
            'projectId': self.project,
            'datasetId': 'mvt_pool',
            'tableId': create_hash(query),
            'token': self.token
        }

    def fetch_mvt_metadata(self, query):
        metadata_query = '''
            WITH q as ({})
            SELECT * FROM q LIMIT 1
        '''.format(query)

        result = self.client.query(metadata_query).to_dataframe()

        if GEOID_KEY not in result.columns:
            raise ValueError('No "geoid" column found.')

        properties = {}
        for column in result.columns:
            if column == GEOM_KEY:
                continue
            dtype = result.dtypes[column]
            properties[column] = {'type': dtypes2vl(dtype)}

        return {
            'idProperty': GEOID_KEY,
            'properties': properties
        }

    def compute_bounds(self, query):
        return [[-73.978909, 40.707749], [-73.909443, 40.764192]]

    def compute_zoom_function(self, query):
        # TODO: implement
        return '''
            (zoom) => {
                if (zoom >= 12) {
                    return 12;
                }
                return null;
            }
        '''

    def trigger_mvt_generation(self, query):
        table_name = create_hash(query)

        if self.check_table_exists(table_name):
            return

        # TODO: optimize query
        generation_query = '''
        CREATE TABLE {0}.{1} AS (
            WITH data AS (
                {2}
            ),
            data_bounds AS (
                SELECT geoid, rmr_tests.ST_Envelope_Box(TO_HEX(ST_ASBINARY(geom))) AS bbox
                FROM data
            ),
            global_bounds AS (
                SELECT
                    MIN(bbox[OFFSET(0)]) as gxmin,
                    MIN(bbox[OFFSET(1)]) as gxmax,
                    MIN(bbox[OFFSET(2)]) as gymin,
                    MIN(bbox[OFFSET(3)]) as gymax
                FROM data_bounds
            ),
            global_bbox AS (
                SELECT tiler.getTilesBBOX(gxmin-0.1, gymin-0.1, gxmax+0.1, gymax+0.1, 12, 16/4096) AS gbbox
                FROM global_bounds
            ),
            tiles_bbox AS (
                SELECT z, x, y, xmin, ymin, xmax, ymax
                FROM global_bbox
                CROSS JOIN UNNEST(global_bbox.gbbox)
            ),
            tiles_xyz AS (
                SELECT b.z, b.x, b.y, a.geoid
                FROM data_bounds a, tiles_bbox b
                WHERE NOT ((bbox[OFFSET(0)] > b.xmax) OR
                           (bbox[OFFSET(1)] < b.xmin) OR
                           (bbox[OFFSET(2)] > b.ymax) OR
                           (bbox[OFFSET(3)] < b.ymin))
            ),
            tiles_geom AS (
                SELECT b.z, b.x, b.y, a.geoid, ST_ASGEOJSON(a.geom) AS geom, a.total_pop
                FROM data a, tiles_xyz b
                WHERE a.geoid = b.geoid
            ),
            tiles_mvt AS (
                SELECT tiler.ST_ASMVT(b.z, b.x, b.y, ARRAY_AGG(TO_JSON_STRING(a)), 0) AS tile
                FROM tiles_geom a, tiles_xyz b
                WHERE a.geoid = b.geoid AND a.x = b.x AND a.y = b.y AND a.z = b.z
                GROUP BY b.z, b.x, b.y
            )
            SELECT z, x, y, mvt
            FROM tiles_mvt
            CROSS JOIN UNNEST(tiles_mvt.tile)
        )
        '''.format(MVT_DATASET, table_name, query)
        self.client.query(generation_query)
        # TODO: polling to check the job

    def estimated_data_size(self, query):
        log.info('Estimating size. This may take a few secods')
        estimation_query = '''
            WITH q as ({})
            SELECT SUM(CHAR_LENGTH(ST_ASTEXT(geom))) AS s FROM q
        '''.format(query)
        estimation_query_job = self.client.query(estimation_query)
        result = estimation_query_job.to_dataframe()
        estimated_size = result.s[0] * 0.425
        if estimated_size < self.DATA_SIZE_LIMIT:
            log.info('DEBUG: small dataset ({:.2f} KB)'.format(estimated_size / 1024))
        else:
            log.info('DEBUG: big dataset ({:.2f} MB)'.format(estimated_size / 1024 / 1024))
        return estimated_size

    def check_table_exists(self, table_name):
        check_query = '''
            SELECT size_bytes FROM `{0}`.__TABLES__ WHERE table_id='{1}'
        '''.format(MVT_DATASET, table_name)
        check_job = self.client.query(check_query)
        result = check_job.to_dataframe()
        return not result.empty

    def get_total_bytes_processed(self, query):
        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        query_job = self.client.query(query, job_config=job_config)
        return query_job.total_bytes_processed

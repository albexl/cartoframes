from google.cloud import bigquery
from google.oauth2.credentials import Credentials as GoogleCredentials
from google.auth.exceptions import RefreshError

from carto.exceptions import CartoException

from ...auth import get_default_credentials


def refresh_client(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RefreshError:
            self.client = self._init_client()
            try:
                return func(self, *args, **kwargs)
            except RefreshError:
                raise CartoException('Something went wrong accessing data. '
                                     'Please, try again in a few seconds or contact support for help.')
    return wrapper


class BigQueryClient(object):

    def __init__(self, project, credentials):
        self._project = project
        self._credentials = credentials or get_default_credentials()
        self.client = self._init_client()

    def _init_client(self):
        google_credentials = GoogleCredentials(self._credentials.get_do_token())

        return bigquery.Client(
            project=self._project,
            credentials=google_credentials)

    @refresh_client
    def upload_dataframe(self, dataframe, schema, tablename, project, dataset):
        dataset_ref = self.client.dataset(dataset, project=project)
        table_ref = dataset_ref.table(tablename)

        schema_wrapped = [bigquery.SchemaField(column, dtype) for column, dtype in schema.items()]

        job_config = bigquery.LoadJobConfig()
        job_config.schema = schema_wrapped

        job = self.client.load_table_from_dataframe(dataframe, table_ref, job_config=job_config)
        job.result()

    @refresh_client
    def query(self, query, **kwargs):
        response = self.client.query(query, **kwargs)

        return response

    @refresh_client
    def download_dataframe(self, project, dataset, table, limit=None, offset=None, file_path=None):
        query = _download_query(project, dataset, table, limit, offset)
        return self.client.query(query).to_dataframe(progress_bar_type='tqdm_notebook')

    @refresh_client
    def download_storage_api(self, project, dataset, table, limit=None, offset=None, file_path=None):
        # pip install google-cloud-bigquery-storage
        from google.cloud.bigquery_storage_v1beta1 import BigQueryStorageClient
        storage_client = BigQueryStorageClient(credentials=GoogleCredentials(self._credentials.get_do_token()))
        query = _download_query(project, dataset, table, limit, offset)
        return self.client.query(query).to_dataframe(progress_bar_type='tqdm_notebook', bqstorage_client=storage_client)

    @refresh_client
    def download_file(self, project, dataset, table, limit=None, offset=None, file_path=None):
        query = _download_query(project, dataset, table, limit, offset)
        rows_iter = self.client.query(query).result()
        with open('/tmp/hola.csv', 'w+') as f:
            for row in rows_iter:
                f.write(','.join([str(i) for i in row.values()]) + "\n")


def _download_query(project, dataset, table, limit=None, offset=None):
    full_table_name = '`{}.{}.{}`'.format(project, dataset, table)
    query = 'SELECT * FROM {}'.format(full_table_name)

    if limit:
        query += ' LIMIT {}'.format(limit)
    if offset:
        query += ' OFFSET {}'.format(offset)

    return query

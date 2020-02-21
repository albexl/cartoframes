from .base_source import BaseSource

SOURCE_TYPE = 'BQMVT'


class BigQuerySource(BaseSource):
    """BigQuerySource

    Args:
        data (dict): project, dataset, tablename, token.
        metadata (str, optional): idProperty, properties.

    """
    def __init__(self, gbq_data, gbq_metadata=None, zoom_func=None):
        if not isinstance(gbq_data, dict):
            raise ValueError('Wrong source input. Valid values are dict.')

        self.type = SOURCE_TYPE
        self.gbq_data = gbq_data
        self.gbq_metadata = gbq_metadata
        self.zoom_func = zoom_func

    def get_geom_type(self):
        # TODO: detect geometry type
        return 'polygon'

    def compute_metadata(self, columns=None):
        # TODO: filter metadata by columns
        self.data = {
            'data': self.gbq_data,
            'metadata': self.gbq_metadata,
            'zoom_func': self.zoom_func
        }
        self.bounds = [[-73.978909, 40.707749], [-73.909443, 40.764192]]  # TODO

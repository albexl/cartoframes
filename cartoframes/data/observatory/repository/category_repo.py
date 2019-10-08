from __future__ import absolute_import

from .entity_repo import EntityRepository


_CATEGORY_ID_FIELD = 'id'


def get_category_repo():
    return _REPO


class CategoryRepository(EntityRepository):

    id_field = _CATEGORY_ID_FIELD

    @classmethod
    def _map_row(cls, row):
        return {
            'id': cls._normalize_field(row, cls.id_field),
            'name': cls._normalize_field(row, 'name')
        }

    @classmethod
    def _get_entity_class(cls):
        from cartoframes.data.observatory.category import Category
        return Category

    def _get_rows(self, field=None, value=None):
        return self.client.get_categories(field, value)


_REPO = CategoryRepository()
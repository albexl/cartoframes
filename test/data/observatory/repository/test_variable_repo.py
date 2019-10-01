import unittest

from cartoframes.data.observatory.variable import Variables, Variable

from cartoframes.exceptions import DiscoveryException

from cartoframes.data.observatory.repository.variable_repo import VariableRepository
from cartoframes.data.observatory.repository.repo_client import RepoClient
from ..examples import test_variable1, test_variables, db_variable1, db_variable2

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class TestVariableRepo(unittest.TestCase):

    @patch.object(RepoClient, 'get_variables')
    def test_get_all(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_variable1, db_variable2]
        repo = VariableRepository()

        # When
        variables = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with(None, None)
        assert isinstance(variables, Variables)
        assert variables == test_variables

    @patch.object(RepoClient, 'get_variables')
    def test_get_all_when_empty(self, mocked_repo):
        # Given
        mocked_repo.return_value = []

        # When
        repo = VariableRepository()
        variables = repo.get_all()

        # Then
        mocked_repo.assert_called_once_with(None, None)
        assert variables is None

    @patch.object(RepoClient, 'get_variables')
    def test_get_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_variable1, db_variable2]
        requested_id = db_variable1['id']

        # When
        repo = VariableRepository()
        variable = repo.get_by_id(requested_id)

        # Then
        mocked_repo.assert_called_once_with('id', requested_id)
        assert isinstance(variable, Variable)
        assert variable == test_variable1

    @patch.object(RepoClient, 'get_variables')
    def test_get_by_id_unknown_fails(self, mocked_repo):
        # Given
        mocked_repo.return_value = []
        requested_id = 'unknown_id'
        repo = VariableRepository()

        # Then
        with self.assertRaises(DiscoveryException):
            repo.get_by_id(requested_id)

    @patch.object(RepoClient, 'get_variables')
    def test_get_by_dataset(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_variable1, db_variable2]
        dataset_id = 'dataset1'
        repo = VariableRepository()

        # When
        variables = repo.get_by_dataset(dataset_id)

        # Then
        mocked_repo.assert_called_once_with('dataset_id', dataset_id)
        assert isinstance(variables, Variables)
        assert variables == test_variables

    @patch.object(RepoClient, 'get_variables')
    def test_get_by_variable_group(self, mocked_repo):
        # Given
        mocked_repo.return_value = [db_variable1, db_variable2]
        variable_group_id = 'vargroup1'
        repo = VariableRepository()

        # When
        variables = repo.get_by_variable_group(variable_group_id)

        # Then
        mocked_repo.assert_called_once_with('variable_group_id', variable_group_id)
        assert isinstance(variables, Variables)
        assert variables == test_variables

    @patch.object(RepoClient, 'get_variables')
    def test_missing_fields_are_mapped_as_None(self, mocked_repo):
        # Given
        mocked_repo.return_value = [{'id': 'variable1'}]
        repo = VariableRepository()

        expected_variables = [{
            'id': 'variable1',
            'name': None,
            'description': None,
            'column_name': None,
            'db_type': None,
            'dataset_id': None,
            'agg_method': None,
            'variable_group_id': None,
            'starred': None,
            'summary_jsonb': None
        }]

        # When
        variables = repo.get_all()

        # Then
        assert variables == expected_variables
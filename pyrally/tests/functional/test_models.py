from mock import patch, Mock
from nose.tools import assert_equal, assert_raises

from pyrally.models import BaseRallyModel


def test_get_attribute_behaviour_getting_attributes_from_dictionary():
    """Test ``__get_attribute__`` behaviour works as expected.

    Test that :py:class:`~pyrally.models.BaseRallyModel` classes look not
    only at attributes held within __dict__, but also to keys in the dictionary
    passed when instantiating.
    """
    test_data = {'_mock_test_data_key': 'test'}
    brm = BaseRallyModel(test_data)
    # check we can get an attribute as usual
    assert_equal(brm.rally_data, test_data)
    # check we can get an attribute from the dictionary of test data
    assert_equal(brm._mock_test_data_key, 'test')
    # check that we still get AttributeErrors when the attribute can't be found
    assert_raises(AttributeError, getattr, brm, 'some_other_attr')


@patch('pyrally.models.API_OBJECT_TYPES')
def test_get_attribute_behaviour_dynamically_loading_objects(API_OBJECT_TYPES):
    """Test ``__get_attribute__`` loads objects dynamically if required.

    Test that :py:class:`~pyrally.models.BaseRallyModel` classes dynamically
    load content using Rally API calls when required.

    It does this when a dictionary is found at the attribute location in the
    dictionary given at instatiation and there is a ``_ref`` key within that
    dictionary.
    """
    mock_baserally_obj = Mock()
    mock_create_from_ref = mock_baserally_obj.create_from_ref

    API_OBJECT_TYPES.get.return_value = mock_baserally_obj
    test_data = {'mock_test_data_key': {'_ref': 'some_reference',
                                         '_type': 'api_type'}}

    brm = BaseRallyModel(test_data)
    # Access an attribute of a remote object.
    remote_fred_attr = brm.mock_test_data_key.fred

    assert_equal(remote_fred_attr, mock_create_from_ref.return_value.fred)
    assert_equal(API_OBJECT_TYPES.get.call_args[0],
                 ('api_type', BaseRallyModel))
    assert_equal(mock_create_from_ref.call_args[0], ('some_reference', ))


@patch('pyrally.models.API_OBJECT_TYPES')
def test_get_attribute_behaviour_dynamically_loading_object_lists(
                                                            API_OBJECT_TYPES):
    """Test ``__get_attribute__`` loads object lists dynamically if required.

    Test that :py:class:`~pyrally.models.BaseRallyModel` classes dynamically
    load sub-content using Rally API calls when required.

    It does this when an attribute is given that is defined in
    ``sub_objects_dynamic_loader``. In such circumstances the mapped key
    should be used and all sub items in that key fetched from the server.
    """
    mock_baserally_obj = Mock()
    mock_create_from_ref = mock_baserally_obj.create_from_ref
    API_OBJECT_TYPES.get.return_value = mock_baserally_obj
    test_data = {'dynamic_sub_object': [{'_ref': 'some_reference_1',
                                         '_type': 'api_type'},
                                        {'_ref': 'some_reference_2',
                                         '_type': 'api_type'},
                                         ]}

    brm = BaseRallyModel(test_data)
    brm.sub_objects_dynamic_loader = {'test_property': 'dynamic_sub_object'}

    dynamic_content = brm.test_property

    # Check that this is now stored in the object for use later.
    assert_equal(dynamic_content, brm._full_sub_objects['test_property'])

    assert_equal(dynamic_content, [mock_create_from_ref.return_value,
                                   mock_create_from_ref.return_value])

    assert_equal(API_OBJECT_TYPES.get.call_count, 2)
    assert_equal(mock_create_from_ref.call_count, 2)
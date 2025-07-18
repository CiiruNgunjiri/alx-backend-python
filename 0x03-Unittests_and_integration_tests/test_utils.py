#!/usr/bin/env python3
"""
Unit tests for the utils module.

Tests include:
- access_nested_map function behavior and exceptions
- get_json function interaction with requests.get
- memoize decorator caching functionality
"""

import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """
    Test suite for utils.access_nested_map.
    """

    @parameterized.expand([
        ({"a": 1},
         ("a",),
         1),

        ({"a": {"b": 2}},
         ("a",),
         {"b": 2}),

        ({"a": {"b": 2}},
         ("a", "b"),
         2),
    ])

    def test_access_nested_map(self, nested_map: dict, 
                               path: tuple,
                               expected) -> None:
        """Test access_nested_map returns expected nested value for given path."""
        self.assertEqual(access_nested_map(nested_map, path),
                         expected)


    @parameterized.expand([
        ({},("a",), "'a'"),

        ({"a": 1}, 
         ("a", "b"),
         "'b'"),
    ])

    def test_access_nested_map_exception(
        self, nested_map: dict, 
        path: tuple, 
        expected_exception_msg: str) -> None:

        """Test access_nested_map raises KeyError with correct message on missing keys."""

        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)

        self.assertEqual(str(context.exception), expected_exception_msg)


class TestGetJson(unittest.TestCase):
    """
    Test suite for utils.get_json.
    """

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])

    @patch("utils.requests.get")
    
    def test_get_json(self, test_url: str, 
                      test_payload: dict,
                      mock_get: Mock) -> None:
    
    """
        Test get_json returns expected payload and calls requests.get with URL.
        """
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response

        result = get_json(test_url)

        mock_get.assert_called_once_with(test_url)

        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """
    Test suite for the utils.memoize decorator.
    """

    def test_memoize(self) -> None:
        """
        Test that memoize caches a method call result and calls
        the decorated method only once even if accessed multiple times.
        """

        class TestClass:
            """
            A test class with a memoized property.
            """

            def a_method(self) -> int:
                """Return a constant integer."""
                return 42

            @memoize
            def a_property(self) -> int:
                """Property decorated with memoize that calls a_method."""
                return self.a_method()

        test_obj = TestClass()

        with patch.object(test_obj, 'a_method', return_value=42) as mock_a_method:
            result1 = test_obj.a_property

            result2 = test_obj.a_property

            self.assertEqual(result1, 42)
            
            self.assertEqual(result2, 42)
            
            mock_a_method.assert_called_once()

if __name__ == "__main__":
    unittest.main()


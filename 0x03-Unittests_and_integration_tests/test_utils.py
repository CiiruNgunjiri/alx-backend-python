#!/usr/bin/env python3
"""
Unit tests for the utils module.

This module tests various utility functions to ensure they behave as expected
under different scenarios, including:

- access_nested_map: Correctly retrieves nested dictionary values and raises
  informative exceptions on missing keys.
- get_json: Properly retrieves JSON payloads from URLs without performing
  actual HTTP requests, using mocks for external calls.
- memoize: Caches the result of a method to avoid repeated expensive calls,
  verified via mock assertions that the target method is only invoked once.

These tests utilize unittest's testing framework, parameterized inputs for
concise multi-case testing, and unittest.mock for patching dependencies.
"""

import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """
    Test suite for utils.access_nested_map function.

    Verifies that given a nested dictionary and a path tuple, the function
    returns the expected nested value. Also ensures that KeyError is raised
    with the correct key name as message when a key is missing at any level.
    """

    @parameterized.expand(
        [
            ({"a": 1}, ("a",), 1),
            ({"a": {"b": 2}}, ("a",), {"b": 2}),
            ({"a": {"b": 2}}, ("a", "b"), 2),
        ]
    )
    def test_access_nested_map(self, nested_map: dict, path: tuple, expected):
        """
        Test that access_nested_map returns the expected value for various
        inputs.

        Args:
            nested_map (dict): Dictionary to traverse.
            path (tuple): Sequence of keys to access nested value.
            expected: The expected value to be returned.
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand(
        [
            ({}, ("a",), "'a'"),
            ({"a": 1}, ("a", "b"), "'b'"),
        ]
    )
    def test_access_nested_map_exception(
        self, nested_map: dict, path: tuple, expected_exception_msg: str
    ):
        """
        Test that access_nested_map raises KeyError with the missing key name.

        Ensures the error message matches exactly the missing key for easier
        debugging and test reliability.

        Args:
            nested_map (dict): Dictionary to traverse.
            path (tuple): Sequence of keys to access nested value.
            expected_exception_msg (str): Expected KeyError message.
        """
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        self.assertEqual(str(context.exception), expected_exception_msg)


class TestGetJson(unittest.TestCase):
    """
    Test suite for utils.get_json function.

    Validates that get_json correctly returns JSON content from a given URL.
    Uses mocking to prevent real HTTP requests and simulate API responses.
    """

    @parameterized.expand(
        [
            ("http://example.com", {"payload": True}),
            ("http://holberton.io", {"payload": False}),
        ]
    )
    @patch("utils.requests.get")
    def test_get_json(
        self, test_url: str, test_payload: dict, mock_get: Mock
    ):
        """
        Test that get_json calls requests.get once and returns the expected
        payload.

        Args:
            test_url (str): The URL to fetch JSON from.
            test_payload (dict): The mocked JSON payload to be returned.
            mock_get (Mock): Mock of requests.get injected by patch.
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

    Ensures that memoize caches the first call result of the decorated method
    and reuses it in subsequent calls without invoking the method again.
    """

    def test_memoize(self):
        """
        Test that memoize caches a_method result when accessed through
        a_property.

        Patches a_method to track its call count and return a controlled value,
        then accesses a_property twice and asserts a_method called once.
        """

        class TestClass:
            """
            Simple test class with a method and memoized property.
            """

            def a_method(self) -> int:
                """Simulates an expensive method returning a constant."""
                return 42

            @memoize
            def a_property(self) -> int:
                """Memoized property calling a_method."""
                return self.a_method()

        test_obj = TestClass()

        with patch.object(test_obj, "a_method", 
                          return_value=42) as mock_a_method:# Access property twice, which should only call a_method once
            result1 = test_obj.a_property
            result2 = test_obj.a_property

            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)

            mock_a_method.assert_called_once()


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""
Test suite for client.GithubOrgClient.

Contains unit tests and integration tests using fixtures and mocks.
"""

import sys
import os
import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos

# Add current directory to sys.path for module imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test GithubOrgClient.org returns expected
        and calls get_json correctly."""
        expected_payload = {"login": org_name}
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)
        result = client.org  # Access memoized property

        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )
        self.assertEqual(result, expected_payload)

    def test_public_repos_url(self):
        """Unit-test the _public_repos_url property."""
        expected_url = "https://api.github.com/orgs/test-org/repos"
        client = GithubOrgClient("test-org")

        with patch.object(GithubOrgClient, "org",
                          new_callable=PropertyMock) as mock_org:
            mock_org.return_value = {"repos_url": expected_url}
            self.assertEqual(client._public_repos_url, expected_url)

    @parameterized.expand([
        (["repo1", "repo2", "repo3"],),
    ])
    @patch("client.get_json")
    def test_public_repos(self, repo_payload, mock_get_json):
        """
        Test public_repos returns expected repo names from mocked payload.
        """
        test_url = "https://api.github.com/orgs/test-org/repos"
        mock_get_json.return_value = [{"name": r} for r in repo_payload]
        client = GithubOrgClient("test-org")

        with patch.object(
            GithubOrgClient,
            "_public_repos_url",
            new_callable=PropertyMock,
            return_value=test_url,
        ) as mock_url:
            repos = client.public_repos()
            self.assertEqual(repos, repo_payload)
            mock_url.assert_called_once()
            mock_get_json.assert_called_once_with(test_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license identifies matching license key correctly."""
        client = GithubOrgClient("test-org")
        result = client.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    [(org_payload, repos_payload, expected_repos, apache2_repos)],
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient using fixture data."""

    @classmethod
    def setUpClass(cls):
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        def json_side_effect(url, *args, **kwargs):
            mock_resp = Mock()
            if url == (
                f"https://api.github.com/orgs/{cls.org_payload['login']}"
            ):
                mock_resp.json.return_value = cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                mock_resp.json.return_value = cls.repos_payload
            else:
                raise ValueError(f"Unmocked url: {url}")
            return mock_resp

        cls.mock_get.side_effect = json_side_effect

    @classmethod
    def tearDownClass(cls):
        cls.get_patcher.stop()

    def test_public_repos(self):
        """public_repos returns expected repo names from payload fixture."""
        client = GithubOrgClient(self.org_payload["login"])
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos filters repos by license correctly."""
        client = GithubOrgClient(self.org_payload["login"])
        filtered_repos = client.public_repos(license="apache-2.0")
        self.assertEqual(filtered_repos, self.apache2_repos)


if __name__ == "__main__":
    unittest.main()

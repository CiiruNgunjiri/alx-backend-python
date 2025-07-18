#!/usr/bin/env python3
"""
Test suite for client.GithubOrgClient.

Contains feature-specific unit tests and integration tests using real payloads.
"""

import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import (
    org_payload,
    repos_payload,
    expected_repos,
    apache2_repos,
)


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """
        Test that org property returns expected payload and calls get_json correctly.

        Because org is memoized as a property, access without parentheses.
        """
        expected_payload = {"login": org_name}
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)
        result = client.org  # access memoized property

        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )
        self.assertEqual(result, expected_payload)

    def test_public_repos_url(self):
        """
        Unit-test the _public_repos_url property.

        Patch the org property to return a known payload and verify the url.
        """
        test_url = "https://api.github.com/orgs/test-org/repos"
        client = GithubOrgClient("test-org")

        with patch.object(
            GithubOrgClient, 
            "org", new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = {"repos_url": test_url}
            self.assertEqual(client._public_repos_url, test_url)

    @parameterized.expand([
        (["repo1", "repo2", "repo3"],),
    ])
    @patch("client.get_json")
    def test_public_repos(self, 
                          repo_payload, 
                          mock_get_json):
        """
        Test public_repos returns expected repo names from a mocked repos payload.

        Use patch to mock _public_repos_url property and get_json function.
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
            expected_repo_names = repo_payload

            self.assertEqual(repos, expected_repo_names)
            mock_url.assert_called_once()
            mock_get_json.assert_called_once_with(test_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, 
         "my_license", True),
        ({"license": {"key": "other_license"}}, 
         "my_license", False),
    ])
    def test_has_license(self, 
                         repo, 
                         license_key, 
                         expected):
        """
        Test that has_license correctly identifies if a repo license matches the license_key.
        """
        client = GithubOrgClient("test-org")
        result = client.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    ("org_payload", 
     "repos_payload", 
     "expected_repos", 
     "apache2_repos"),
    [(org_payload, 
      repos_payload, 
      expected_repos, 
      apache2_repos)],
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration tests for GithubOrgClient with real payload fixtures.

    Mocks requests.get to provide controlled org and repos data without external HTTP requests.
    """

    @classmethod
    def setUpClass(cls):
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        def json_side_effect(url, *args, **kwargs):
            mock_resp = Mock()
            if url == (
                f"https://api.github.com/orgs/{cls.org_payload['login']}"):
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
        """Test public_repos returns expected list of repo names from fixture."""
        client = GithubOrgClient(self.org_payload["login"])
        self.assertEqual(client.public_repos(), 
                         self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos filters by license correctly from fixture."""
        client = GithubOrgClient(self.org_payload["login"])
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos,
        )


if __name__ == "__main__":
    unittest.main()

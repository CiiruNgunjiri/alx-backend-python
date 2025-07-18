#!/usr/bin/env python3
"""
Unit and integration tests for client.GithubOrgClient.

Tests include:
- org method unit tests with mock
- _public_repos_url property unit test
- public_repos method unit tests with mocked dependencies
- has_license method unit test
- integration tests mocking external requests with real payloads from fixtures
"""

import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos  # Your fixtures


class TestGithubOrgClient(unittest.TestCase):
    """
    Unit tests for GithubOrgClient.
    """

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name: str, mock_get_json: Mock) -> None:
        """
        Test org method returns expected payload and calls get_json once.
        """
        expected_payload = {"login": org_name}
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)
        result = client.org()

        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")
        self.assertEqual(result, expected_payload)

    def test_public_repos_url(self) -> None:
        """
        Test _public_repos_url property returns repos_url from org payload.
        """
        test_url = "https://api.github.com/orgs/test-org/repos"
        with patch.object(GithubOrgClient, "org", new_callable=PropertyMock) as mock_org:
            mock_org.return_value = {"repos_url": test_url}
            client = GithubOrgClient("test-org")
            self.assertEqual(client._public_repos_url, test_url)

    @patch("client.get_json")
    @parameterized.expand([
        (["repo1", "repo2", "repo3"],),
    ])
    def test_public_repos(self, repo_payload, mock_get_json):
        """
        Test that public_repos returns expected list of repo names.
        """
        test_url = "https://api.github.com/orgs/test-org/repos"
        with patch.object(
            GithubOrgClient, "_public_repos_url", new_callable=PropertyMock,
            return_value=test_url,
        ) as mock_public_repos_url:
            mock_get_json.return_value = [{"name": r} for r in repo_payload]
            client = GithubOrgClient("test-org")

            result = client.public_repos()

            self.assertEqual(result, repo_payload)
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(test_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo: dict, license_key: str, expected: bool) -> None:
        """
        Test has_license returns True when license key matches, else False.
        """
        client = GithubOrgClient("test-org")
        self.assertEqual(client.has_license(repo, license_key), expected)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    [
        (org_payload, repos_payload, expected_repos, apache2_repos),
    ],
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration tests for GithubOrgClient using real payloads and mocked requests.get.

    Uses setUpClass and tearDownClass for patch lifecycle.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        def json_side_effect(url, *args, **kwargs):
            if url == "https://api.github.com/orgs/google":
                mock_resp = Mock()
                mock_resp.json.return_value = cls.org_payload
                return mock_resp
            if url == "https://api.github.com/orgs/google/repos":
                mock_resp = Mock()
                mock_resp.json.return_value = cls.repos_payload
                return mock_resp
            raise ValueError(f"Unmocked url: {url}")

        cls.mock_get.side_effect = json_side_effect

    @classmethod
    def tearDownClass(cls) -> None:
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """
        Test public_repos returns expected repo names.
        """
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self) -> None:
        """
        Test public_repos filters repos correctly by license.
        """
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(license="apache-2.0"), self.apache2_repos)


if __name__ == "__main__":
    unittest.main()

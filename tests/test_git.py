"""Tests for git URL validation and repository operations."""

import pytest
from shinkuro.remote.git import extract_user_repo


class TestExtractUserRepo:
    """Tests for extract_user_repo function."""

    def test_github_https_url(self):
        """Test parsing GitHub HTTPS URL."""
        user, repo = extract_user_repo("https://github.com/DiscreteTom/shinkuro.git")
        assert user == "DiscreteTom"
        assert repo == "shinkuro"

    def test_github_ssh_url(self):
        """Test parsing GitHub SSH URL."""
        user, repo = extract_user_repo("git@github.com:DiscreteTom/shinkuro.git")
        assert user == "DiscreteTom"
        assert repo == "shinkuro"

    def test_gitlab_url(self):
        """Test parsing GitLab URL."""
        user, repo = extract_user_repo("https://gitlab.com/user/project.git")
        assert user == "user"
        assert repo == "project"

    def test_url_without_git_extension(self):
        """Test parsing URL without .git extension."""
        user, repo = extract_user_repo("https://github.com/DiscreteTom/shinkuro")
        assert user == "DiscreteTom"
        assert repo == "shinkuro"

    def test_invalid_url_missing_parts(self):
        """Test that URLs missing user or repo raise ValueError."""
        with pytest.raises(ValueError, match="Cannot extract user/repo"):
            extract_user_repo("https://github.com/")

    def test_path_traversal_in_username_blocked(self):
        """Test that path traversal in username is blocked."""
        # giturlparse fails to parse these malformed URLs, we catch and convert to ValueError
        with pytest.raises(ValueError, match="Cannot extract user/repo"):
            extract_user_repo("https://github.com/../etc/shinkuro.git")

    def test_path_traversal_in_repo_blocked(self):
        """Test that path traversal in repo name is blocked."""
        # giturlparse fails to parse these malformed URLs, we catch and convert to ValueError
        with pytest.raises(ValueError, match="Cannot extract user/repo"):
            extract_user_repo("https://github.com/user/../etc.git")

    def test_path_separator_in_username_blocked(self):
        """Test that path separators in username are blocked."""
        # Construct a malformed URL that might bypass giturlparse
        # This tests our defense-in-depth validation
        with pytest.raises(ValueError):
            extract_user_repo("https://github.com/user/extra/repo.git")

    def test_dot_in_repo_name_allowed(self):
        """Test that legitimate dots in repo names are allowed."""
        user, repo = extract_user_repo("https://github.com/user/my.repo.git")
        assert user == "user"
        assert repo == "my.repo"

    def test_hyphen_in_names_allowed(self):
        """Test that hyphens in user and repo names are allowed."""
        user, repo = extract_user_repo("https://github.com/my-user/my-repo.git")
        assert user == "my-user"
        assert repo == "my-repo"

    def test_underscore_in_names_allowed(self):
        """Test that underscores in names are allowed."""
        user, repo = extract_user_repo("https://github.com/my_user/my_repo.git")
        assert user == "my_user"
        assert repo == "my_repo"

    def test_empty_string_raises_error(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError):
            extract_user_repo("")

    def test_null_byte_in_url_blocked(self):
        """Test that null bytes in URL are blocked."""
        with pytest.raises(ValueError):
            extract_user_repo("https://github.com/user\x00/repo.git")

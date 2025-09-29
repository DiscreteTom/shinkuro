# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Replace `GITHUB_REPO` environment variable with `GIT_URL` for broader git repository support
- Update cache directory structure from `~/.shinkuro/remote/github/{owner}/{repo}` to `~/.shinkuro/remote/git/{user}/{repo}`
- Support any git URL format (GitHub, GitLab, SSH, HTTPS with credentials)

## [0.1.0] - 2025-09-29

### Added

- Local file mode
- GitHub mode

[unreleased]: https://github.com/DiscreteTom/shinkuro/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/DiscreteTom/shinkuro/releases/tag/v0.1.0

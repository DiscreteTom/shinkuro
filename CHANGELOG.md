# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2025-09-30

### Added

- Support for prompt arguments with variable replacement using `{variable}` format in templates
- Escape literal brackets using double brackets (`{{var}}`)
- Support for `title` field in frontmatter (defaults to filename)

### Changed

- Remove tag `local` from all prompts, add tag `shinkuro`.

## [0.2.0] - 2025-09-29

### Changed

- Replace `GITHUB_REPO` environment variable with `GIT_URL` for broader git repository support
- Update cache directory structure from `~/.shinkuro/remote/github/{owner}/{repo}` to `~/.shinkuro/remote/git/{user}/{repo}`
- Support any git URL format (GitHub, GitLab, SSH, HTTPS with credentials)

## [0.1.0] - 2025-09-29

### Added

- Local file mode
- GitHub mode

[unreleased]: https://github.com/DiscreteTom/shinkuro/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/DiscreteTom/shinkuro/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/DiscreteTom/shinkuro/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/DiscreteTom/shinkuro/releases/tag/v0.1.0

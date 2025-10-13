# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.3] - 2025-10-13

### Added

- Support for `VARIABLE_FORMAT` environment variable to choose between `{var}` (brace) and `$var` (dollar) syntax
- Support for `AUTO_DISCOVER_ARGS` environment variable to auto-discover template variables as required arguments
- Support for `SKIP_FRONTMATTER` environment variable to skip frontmatter processing and use raw markdown content

## [0.3.2] - 2025-10-11

### Fixed

- Fix git repository cache path generation to use repository owner instead of protocol user (was creating `$CACHE_DIR/git/git/repo` instead of `$CACHE_DIR/git/owner/repo`)

## [0.3.1] - 2025-10-08

### Added

- Comprehensive validation and warning system for frontmatter fields
- Automatic type conversion for non-string fields with stderr warnings
- Validation for argument names (must contain only alphanumeric and underscore characters)
- Required validation for argument names (skip arguments without valid names)
- Detailed error messages for invalid folder paths, unsafe template variables, and processing exceptions

### Security

- Replace unsafe dynamic code execution with safe MarkdownPrompt class for prompt rendering
- Add validation to prevent format string injection attacks in template variables
- Only allow alphanumeric and underscore characters in variable names (e.g., `{name}`, `{project_name}`)
- Block dangerous expressions like `{name.__class__}` or `{name[0]}` at file loading time

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

[unreleased]: https://github.com/DiscreteTom/shinkuro/compare/v0.3.3...HEAD
[0.3.3]: https://github.com/DiscreteTom/shinkuro/compare/v0.3.2...v0.3.3
[0.3.2]: https://github.com/DiscreteTom/shinkuro/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/DiscreteTom/shinkuro/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/DiscreteTom/shinkuro/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/DiscreteTom/shinkuro/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/DiscreteTom/shinkuro/releases/tag/v0.1.0

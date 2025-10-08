# Shinkuro - Prompt synchronization MCP server

![PyPI - Version](https://img.shields.io/pypi/v/shinkuro)

Loads markdown files from a local folder or git repository and serves them as [MCP Prompts](https://modelcontextprotocol.io/specification/2025-06-18/server/prompts).

Useful when you need to share prompts across organizations.

## Usage

**IMPORTANT**: make sure your MCP client supports the MCP Prompts capability. See the [feature support matrix](https://modelcontextprotocol.io/clients#feature-support-matrix).

### Local Files

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "shinkuro": {
      "command": "uvx",
      "args": ["shinkuro"],
      "env": {
        "FOLDER": "/path/to/prompts"
      }
    }
  }
}
```

### Git Repository

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "shinkuro": {
      "command": "uvx",
      "args": ["shinkuro"],
      "env": {
        "GIT_URL": "https://github.com/owner/repo.git",
        "FOLDER": "prompts" // optional, subfolder within git repo
      }
    }
  }
}
```

> This will clone the repository into a local cache dir. Make sure you have correct permission.

### Environment Variables

- `FOLDER`: Path to local folder containing markdown files, or subfolder within git repo
- `GIT_URL`: Git repository URL (supports GitHub, GitLab, SSH, HTTPS with credentials)
- `CACHE_DIR`: Directory to cache cloned repositories (optional, defaults to `~/.shinkuro/remote`)
- `AUTO_PULL`: Whether to pull latest changes if repo exists locally (optional, defaults to `false`)

## Prompt Loading

Each markdown file in the specified folder (including nested folders) is loaded as a prompt.

Example folder structure:

```
my-prompts/
├── think.md
└── dev/
     ├── code-review.md
     └── commit.md
```

The example above will be loaded to 3 prompts: `think`, `code-review` and `commit`.

## Example Prompt Files

### Simplest

```markdown
Commit to git using conventional commit.
```

### Prompt with Metadata

```markdown
---
name: "code-review" # optional, defaults to filename
title: "Code Review Assistant" # optional, defaults to filename
description: "" # optional, defaults to file path
---

# Code Review

Please review this code for best practices and potential issues.
```

### Prompt with Arguments

```markdown
---
name: "greeting"
description: "Generate a personalized greeting message"
arguments:
  - name: "user"
    description: "Name of the user"
    # no default = required parameter
  - name: "project"
    description: "Project name"
    default: "MyApp"
---

Say: Hello {user}! Welcome to {project}. Hope you enjoy your stay!
```

Variables like `{user}` and `{project}` will be replaced with actual values when the prompt is retrieved. Use `{{var}}` (double brackets) to escape and display literal brackets.

## Example Prompt Repositories

- [DiscreteTom/prompts](https://github.com/DiscreteTom/prompts).

## Development

### Setup

Install development dependencies:

```fish
uv sync --dev
```

### Code Quality

```fish
# Format code
uv run black .

# Lint
uv run ruff check --fix .

# Type check
uv run pyright
```

### Testing

Run the test suite:

```fish
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=shinkuro --cov-report=html

# Run specific test file
uv run pytest tests/test_security.py
```

The test suite includes:
- **Security validation tests** - Path traversal prevention, identifier validation
- **Server tests** - SafeFormatter, dynamic prompt generation
- **Git URL tests** - URL parsing and validation
- **File scanning tests** - Markdown processing and error handling
- **Integration tests** - End-to-end server functionality

See [tests/README.md](./tests/README.md) for detailed testing documentation.

### Pre-commit Hooks

Install pre-commit hooks to run quality checks automatically:

```fish
uv run pre-commit install
```

## Security

This project includes security measures to prevent:
- **Path traversal attacks** via environment variables
- **Code injection** through dynamic function generation
- **Format string attacks** via template substitution

See the [security module](./src/shinkuro/security.py) and [test suite](./tests/) for implementation details.

## [CHANGELOG](./CHANGELOG.md)

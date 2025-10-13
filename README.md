# Shinkuro - Universal prompt loader MCP server

[![PyPI - Version](https://img.shields.io/pypi/v/shinkuro)](https://pypi.org/project/shinkuro/)
![Codecov](https://img.shields.io/codecov/c/github/DiscreteTom/shinkuro)

Loads markdown files from a local folder or git repository and serves them as [MCP Prompts](https://modelcontextprotocol.io/specification/2025-06-18/server/prompts).

Useful for loading prompts from various sources and formats into your MCP-enabled applications, and sharing prompts across organizations.

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

### Remote Git Repository

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

> Private repositories are supported, e.g. `"GIT_URL": "git@github.com:DiscreteTom/shinkuro.git"` (with SSH keys), `"GIT_URL": "https://<username>:<PAT>@github.com/owner/repo.git"` (with personal access token)

### Use with [Spec-Kit](https://github.com/github/spec-kit)

First, move spec-kit prompts into `./.shinkuro/prompts` folder.

Then add to your MCP client configuration:

```json
{
  "mcpServers": {
    "shinkuro": {
      "command": "uvx",
      "args": ["shinkuro"],
      "env": {
        "FOLDER": "./.shinkuro/prompts",
        "VARIABLE_FORMAT": "dollar",
        "AUTO_DISCOVER_ARGS": "true",
        "SKIP_FRONTMATTER": "true"
      }
    }
  }
}
```

This will expose spec-kit instructions as MCP prompts.

### Environment Variables

- `FOLDER`: Path to local folder containing markdown files, or subfolder within git repo
- `GIT_URL`: Git repository URL (supports GitHub, GitLab, SSH, HTTPS with credentials)
- `CACHE_DIR`: Directory to cache remote repositories (optional, defaults to `~/.shinkuro/remote`)
- `AUTO_PULL`: Whether to refresh local cache on startup (optional, defaults to `false`)
- `VARIABLE_FORMAT`: Template variable format (optional, defaults to `brace`)
  - `brace`: Use `{var}` syntax (default)
  - `dollar`: Use `$var` syntax
- `AUTO_DISCOVER_ARGS`: Auto-discover template variables as required arguments (optional, defaults to `false`)
- `SKIP_FRONTMATTER`: Skip frontmatter processing and use raw markdown content (optional, defaults to `false`)

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

Variables like `{user}` and `{project}` will be replaced with actual values when the prompt is retrieved.

Use `{{var}}` (double brackets) to escape and display literal brackets when using brace formatter.

> **Different Variable Formats:**
>
> - `VARIABLE_FORMAT=brace` (default): `{user}`, `{project}`
> - `VARIABLE_FORMAT=dollar`: `$user`, `$project`

## Example Prompt Repositories

- [DiscreteTom/prompts](https://github.com/DiscreteTom/prompts).

## [CHANGELOG](./CHANGELOG.md)

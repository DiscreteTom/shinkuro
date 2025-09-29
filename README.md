# Shinkuro - Prompt synchronization MCP server

![PyPI - Version](https://img.shields.io/pypi/v/shinkuro)

Loads markdown files from a local folder or GitHub repository and serves them as [prompts](https://modelcontextprotocol.io/specification/2025-06-18/server/prompts).

## Usage

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
        "FOLDER": "" // optional, subfolder within git repo
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

## Prompts

### Loading

Each markdown file in the specified folder is loaded as a prompt.

Example folder structure:

```
my-prompts/
├── code-review.md
├── dev.md
└── commit.md
```

### Example Prompt File

```markdown
---
name: "" # optional, defaults to filename
description: "" # optional, defaults to file path
---

# Prompt Content

Your prompt content here...
```

# Shinkuro

Prompt management and synchronization MCP server that loads markdown files from a folder and serves them as prompts.

## Usage

### MCP Client Configuration

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

Or use a GitHub repository:

```json
{
  "mcpServers": {
    "shinkuro": {
      "command": "uvx",
      "args": ["shinkuro"],
      "env": {
        "GITHUB_REPO": "owner/repo",
        "FOLDER": "" // optional, subfolder of the github repo
      }
    }
  }
}
```

### Environment Variables

- `FOLDER`: Path to local folder containing markdown files, or subfolder within GitHub repo
- `GITHUB_REPO`: GitHub repository in format "owner/repo"
- `CACHE_DIR`: Directory to cache cloned repositories (optional, defaults to `~/.shinkuro/remote`)
- `AUTO_PULL`: Whether to pull latest changes if repo exists locally (optional, defaults to false)

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

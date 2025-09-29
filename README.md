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

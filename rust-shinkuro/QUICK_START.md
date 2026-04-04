# Quick Start Guide

Get up and running with Shinkuro (Rust) in 5 minutes!

## 1. Prerequisites

```bash
# Check if Rust is installed
rustc --version

# If not, install Rust:
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

## 2. Build

```bash
cd rust-shinkuro
cargo build --release
```

⏱️ First build takes 2-5 minutes. Subsequent builds are much faster!

## 3. Test

```bash
# Run tests
cargo test

# Try with example prompts
./target/release/shinkuro --folder examples/prompts
```

The server will start and communicate via stdin/stdout (MCP protocol).

## 4. Configure MCP Client

Add to your MCP client configuration (e.g., Claude Desktop):

### Option A: Local Prompts

```json
{
  "mcpServers": {
    "shinkuro": {
      "command": "/full/path/to/rust-shinkuro/target/release/shinkuro",
      "args": [],
      "env": {
        "FOLDER": "/path/to/your/prompts"
      }
    }
  }
}
```

### Option B: Git Repository

```json
{
  "mcpServers": {
    "shinkuro": {
      "command": "/full/path/to/rust-shinkuro/target/release/shinkuro",
      "args": [],
      "env": {
        "GIT_URL": "https://github.com/owner/repo.git",
        "FOLDER": "prompts"
      }
    }
  }
}
```

## 5. Create Your First Prompt

Create a file `my-prompts/hello.md`:

```markdown
---
name: hello
description: Simple greeting
arguments:
  - name: name
    description: Your name
---

Hello {name}! Welcome to Shinkuro!
```

## 6. Use the Prompt

In your MCP client:
1. Look for available prompts
2. Select "hello"
3. Provide argument: `name = "World"`
4. Get: "Hello World! Welcome to Shinkuro!"

## Common Commands

```bash
# Show help
./target/release/shinkuro --help

# Show version
./target/release/shinkuro --version

# Use dollar-style variables ($var)
./target/release/shinkuro --folder /path --variable-format dollar

# Auto-discover arguments (no frontmatter needed)
./target/release/shinkuro --folder /path --auto-discover-args

# Skip frontmatter completely
./target/release/shinkuro --folder /path --skip-frontmatter

# Pull latest from git on startup
./target/release/shinkuro --git-url https://... --auto-pull
```

## Prompt File Format

### Minimal
```markdown
This is a simple prompt with no arguments.
```

### With Arguments
```markdown
---
name: greeting
description: Personalized greeting
arguments:
  - name: user
    description: User's name
  - name: project
    description: Project name
    default: MyApp
---

Hello {user}! Welcome to {project}.
```

### Dollar Style
```markdown
---
name: greeting
arguments:
  - name: user
---

Hello $user!
```

Use `--variable-format dollar` to render.

## Template Variables

### Brace Style (Default)
- `{variable}` - replaced with value
- `{{literal}}` - escaped, renders as `{literal}`

### Dollar Style
- `$variable` - replaced with value
- `$$` - escaped, renders as `$`

## Directory Structure

```
my-prompts/
├── general/
│   ├── greeting.md
│   └── farewell.md
├── dev/
│   ├── code-review.md
│   └── commit-msg.md
└── docs/
    └── summary.md
```

All `.md` files are loaded recursively!

## Environment Variables

Instead of command-line arguments, use environment variables:

```bash
export FOLDER="/path/to/prompts"
export VARIABLE_FORMAT="dollar"
export AUTO_DISCOVER_ARGS="true"

./target/release/shinkuro
```

## Troubleshooting

### "Command not found: cargo"
Install Rust: https://rustup.rs

### Build fails with OpenSSL error
```bash
# Linux
sudo apt-get install libssl-dev pkg-config

# macOS
brew install openssl
```

### "Folder does not exist" warning
Check that the path is correct and accessible.

### Git clone fails
- Check git URL is correct
- For private repos, use SSH or HTTPS with token
- Ensure git is installed and configured

### No prompts loaded
- Check markdown files have `.md` extension
- Verify frontmatter YAML is valid
- Check argument names in frontmatter match template variables

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [COMPARISON.md](COMPARISON.md) to understand Python vs Rust differences
- See [INSTALL.md](INSTALL.md) for advanced installation options
- Browse `examples/prompts/` for more examples

## Getting Help

1. Run with `--help` flag
2. Check documentation files in this directory
3. Review example prompts in `examples/prompts/`
4. Open an issue on GitHub

## Tips

- 🚀 **Performance**: Rust binary starts in ~15ms vs ~300ms for Python
- 💾 **Memory**: Uses ~5MB vs ~40MB for Python version
- 📦 **Portable**: Single binary, no runtime dependencies
- 🔒 **Safe**: Memory safe by design
- 🔄 **Compatible**: Same CLI and MCP protocol as Python version

Happy prompting! 🎉

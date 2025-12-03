# Shinkuro - Rust Implementation

This is a Rust implementation of the Shinkuro MCP server, providing equivalent functionality to the Python version.

## Features

The Rust implementation maintains all capabilities from the Python version:

- **CLI Application**: Serves as an MCP (Model Context Protocol) server
- **Local & Remote Loading**: Load prompts from both local markdown files and remote git repositories
- **YAML Frontmatter Parsing**: Extract prompt metadata (name, description, arguments with types and descriptions, defaults)
- **Template Variable Substitution**: Support both brace-style `{variable}` and dollar-style `$variable` formatting
- **Git Operations**: Clone and update remote repositories to a local cache
- **Recursive Scanning**: Scan directories recursively for markdown files
- **Argument Validation**: Validate required arguments and apply default values for optional arguments
- **MCP Protocol**: Full MCP server capabilities for prompt discovery and rendering

## Building

### Prerequisites

- Rust 1.70 or later (install from [rustup.rs](https://rustup.rs))

### Build Instructions

```bash
# Clone the repository (if not already done)
cd rust-shinkuro

# Build in release mode
cargo build --release

# The binary will be at target/release/shinkuro
```

### Run Tests

```bash
cargo test
```

## Usage

The Rust implementation provides the same command-line interface as the Python version:

```bash
# Show help
./target/release/shinkuro --help

# Show version
./target/release/shinkuro --version

# Load from local folder
./target/release/shinkuro --folder /path/to/prompts

# Load from git repository
./target/release/shinkuro --git-url https://github.com/owner/repo.git

# Load from git repository with subfolder
./target/release/shinkuro --git-url https://github.com/owner/repo.git --folder prompts

# With auto-pull enabled
./target/release/shinkuro --git-url https://github.com/owner/repo.git --auto-pull

# With dollar-style variables
./target/release/shinkuro --folder /path/to/prompts --variable-format dollar

# With auto-discovery of arguments
./target/release/shinkuro --folder /path/to/prompts --auto-discover-args

# Skip frontmatter processing
./target/release/shinkuro --folder /path/to/prompts --skip-frontmatter
```

## MCP Client Configuration

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "shinkuro": {
      "command": "/path/to/rust-shinkuro/target/release/shinkuro",
      "args": [],
      "env": {
        "FOLDER": "/path/to/prompts"
      }
    }
  }
}
```

Or with git URL:

```json
{
  "mcpServers": {
    "shinkuro": {
      "command": "/path/to/rust-shinkuro/target/release/shinkuro",
      "args": [],
      "env": {
        "GIT_URL": "https://github.com/owner/repo.git",
        "FOLDER": "prompts",
        "AUTO_PULL": "true"
      }
    }
  }
}
```

## Environment Variables

All command-line options can also be set via environment variables:

- `FOLDER`: Path to local folder or subfolder within git repo
- `GIT_URL`: Git repository URL
- `CACHE_DIR`: Directory to cache remote repositories (default: `~/.shinkuro/remote`)
- `AUTO_PULL`: Whether to refresh local cache on startup (true/false)
- `VARIABLE_FORMAT`: Template variable format (`brace` or `dollar`)
- `AUTO_DISCOVER_ARGS`: Auto-discover template variables as required arguments (true/false)
- `SKIP_FRONTMATTER`: Skip frontmatter processing (true/false)

## Project Structure

```
rust-shinkuro/
├── Cargo.toml          # Rust project configuration and dependencies
├── README.md           # This file
└── src/
    ├── main.rs         # Entry point and main function
    ├── cli.rs          # Command-line argument parsing
    ├── model.rs        # Data models (Argument, PromptData)
    ├── formatters.rs   # Template formatters (Brace, Dollar)
    ├── file.rs         # Markdown file scanning and parsing
    ├── git.rs          # Git repository operations
    ├── loader.rs       # Folder path resolution
    └── mcp.rs          # MCP protocol server implementation
```

## Dependencies

The Rust implementation uses the following key dependencies:

- **clap**: Command-line argument parsing
- **tokio**: Async runtime
- **serde/serde_json**: JSON serialization
- **yaml-front-matter/serde_yaml**: YAML frontmatter parsing
- **git2**: Git operations
- **regex**: Template variable extraction
- **walkdir**: Recursive directory traversal
- **anyhow/thiserror**: Error handling

## Differences from Python Version

While maintaining functional equivalence, the Rust implementation has these differences:

1. **Performance**: Rust version is compiled to native code and should be faster
2. **Memory Safety**: Rust's ownership system provides memory safety without garbage collection
3. **Static Typing**: All types are checked at compile time
4. **No External Python Dependencies**: Standalone binary with no runtime dependencies
5. **Concurrent Safety**: Rust's type system ensures thread safety

## Development

### Code Organization

The code is organized into modules following Rust best practices:

- **cli**: Command-line interface using `clap`
- **model**: Data structures for prompts and arguments
- **formatters**: Template variable substitution logic
- **file**: File system operations and markdown parsing
- **git**: Git repository cloning and updating
- **loader**: Path resolution for local and remote sources
- **mcp**: MCP protocol implementation

### Adding Features

To add new features:

1. Add new dependencies to `Cargo.toml` if needed
2. Create new modules or extend existing ones
3. Update the CLI in `cli.rs` if adding new options
4. Add tests in the relevant module

### Testing

Run tests with:

```bash
# Run all tests
cargo test

# Run tests with output
cargo test -- --nocapture

# Run specific test
cargo test test_name
```

## Troubleshooting

### Build Errors

If you encounter build errors:

1. Ensure Rust is up to date: `rustup update`
2. Clean and rebuild: `cargo clean && cargo build --release`
3. Check that all dependencies are available

### Git Repository Access

For private repositories:

- **SSH**: Ensure SSH keys are configured (`git@github.com:owner/repo.git`)
- **HTTPS**: Use personal access token in URL (`https://username:token@github.com/owner/repo.git`)

### Path Expansion

The `~` character in paths is expanded to the user's home directory automatically.

## License

MIT License - Same as the Python version

## Version

Current version: 0.3.5 (matching Python implementation)

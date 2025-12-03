# Installation Guide

## Quick Start

### 1. Install Rust

If you don't have Rust installed, install it using rustup:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

Follow the prompts and then restart your terminal or run:

```bash
source $HOME/.cargo/env
```

Verify installation:

```bash
rustc --version
cargo --version
```

### 2. Build Shinkuro

```bash
cd rust-shinkuro
./build.sh
```

Or manually:

```bash
cargo build --release
```

### 3. Test the Installation

```bash
# Run tests
cargo test

# Check version
./target/release/shinkuro --version

# Try with example prompts
./target/release/shinkuro --folder examples/prompts
```

## System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Rust**: Version 1.70 or later
- **Disk Space**: ~500MB for Rust toolchain and dependencies
- **Memory**: 1GB minimum for compilation

## Installation Methods

### Method 1: From Source (Recommended)

```bash
# Clone the repository
cd /path/to/shinkuro/rust-shinkuro

# Build release version
cargo build --release

# Binary will be at: target/release/shinkuro
```

### Method 2: Install with Cargo

```bash
# Install to ~/.cargo/bin
cargo install --path .

# Now you can run from anywhere
shinkuro --version
```

### Method 3: Create System-wide Installation

```bash
# Build release
cargo build --release

# Copy to system bin directory (requires sudo)
sudo cp target/release/shinkuro /usr/local/bin/

# Verify
which shinkuro
shinkuro --version
```

## Platform-Specific Notes

### Linux

All dependencies should build automatically. If you encounter build errors:

```bash
# Install build essentials
sudo apt-get install build-essential pkg-config libssl-dev

# Or on Fedora/RHEL
sudo dnf install gcc openssl-devel
```

### macOS

Requires Xcode command line tools:

```bash
xcode-select --install
```

### Windows

1. Install Visual Studio Build Tools or Visual Studio with C++ development tools
2. Install Rust using rustup-init.exe from rustup.rs
3. Build in PowerShell or cmd:

```powershell
cargo build --release
```

## Troubleshooting

### Build Fails with OpenSSL Errors

```bash
# Linux
sudo apt-get install libssl-dev pkg-config

# macOS
brew install openssl
```

### Git2 Dependency Fails

The git2 crate requires libgit2. If it fails to build:

```bash
# Linux
sudo apt-get install libgit2-dev

# macOS
brew install libgit2
```

### Slow Compilation

Rust compilation can be slow on first build. This is normal. Subsequent builds will be faster.

To speed up:

```bash
# Use more CPU cores
cargo build --release -j $(nproc)
```

## Updating

To update the Rust toolchain:

```bash
rustup update
```

To rebuild after code changes:

```bash
cargo build --release
```

To clean and rebuild:

```bash
cargo clean
cargo build --release
```

## Uninstalling

If installed with cargo:

```bash
cargo uninstall shinkuro
```

If copied to system bin:

```bash
sudo rm /usr/local/bin/shinkuro
```

To remove build artifacts:

```bash
cargo clean
```

## Development Setup

For development with hot reloading:

```bash
# Install cargo-watch
cargo install cargo-watch

# Auto-rebuild on changes
cargo watch -x 'build'

# Auto-test on changes
cargo watch -x 'test'
```

## Next Steps

After installation:

1. Read [README.md](README.md) for usage examples
2. Try the example prompts in `examples/prompts/`
3. Configure your MCP client to use the Shinkuro server
4. Create your own markdown prompts

## Getting Help

If you encounter issues:

1. Check this installation guide
2. Review [README.md](README.md) for usage help
3. Check Rust version: `rustc --version` (should be 1.70+)
4. Check build logs for specific error messages
5. Open an issue on the GitHub repository

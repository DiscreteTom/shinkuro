#!/bin/bash
# Build script for Rust Shinkuro

set -e

echo "Building Shinkuro (Rust)..."
cargo build --release

echo ""
echo "Build successful!"
echo "Binary location: target/release/shinkuro"
echo ""
echo "Run tests with: cargo test"
echo "Run the server: ./target/release/shinkuro --help"

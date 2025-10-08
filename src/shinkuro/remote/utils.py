"""Remote repository utilities."""

import os
from pathlib import Path


def get_cache_dir() -> Path:
    """Get the cache directory for storing cloned repositories."""
    cache_dir = os.getenv("CACHE_DIR")
    if cache_dir:
        # Validate CACHE_DIR to prevent path traversal
        try:
            cache_path = Path(cache_dir).resolve()
            # Ensure it's an absolute path
            if not cache_path.is_absolute():
                raise ValueError("CACHE_DIR must be an absolute path")
            return cache_path
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Invalid CACHE_DIR: {e}")

    # Default to ~/.shinkuro/remote
    home = Path.home()
    return home / ".shinkuro" / "remote"

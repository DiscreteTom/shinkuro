"""Remote repository utilities."""

import os
from pathlib import Path


def get_cache_dir() -> Path:
    """Get the cache directory for storing cloned repositories."""
    cache_dir = os.getenv("CACHE_DIR")
    if cache_dir:
        return Path(cache_dir)

    # Default to ~/.shinkuro/remote
    home = Path.home()
    return home / ".shinkuro" / "remote"

use crate::git::{clone_or_update_repo, get_local_cache_path};
use anyhow::{Context, Result};
use std::path::{Path, PathBuf};

/// Determine the folder path to scan for prompts
pub fn get_folder_path(
    folder: Option<&str>,
    git_url: Option<&str>,
    cache_dir: &Path,
    auto_pull: bool,
) -> Result<PathBuf> {
    // Expand tilde in cache_dir
    let cache_dir = if cache_dir.starts_with("~") {
        let home = dirs::home_dir().context("Could not determine home directory")?;
        let path_str = cache_dir.to_string_lossy();
        let without_tilde = path_str.strip_prefix("~/").unwrap_or(&path_str);
        home.join(without_tilde)
    } else {
        cache_dir.to_path_buf()
    };
    
    if let Some(git_url) = git_url {
        let repo_path = get_local_cache_path(git_url, &cache_dir)?;
        clone_or_update_repo(git_url, &repo_path, auto_pull)?;
        
        if let Some(folder) = folder {
            // Use folder as subfolder within the repo
            Ok(repo_path.join(folder))
        } else {
            Ok(repo_path)
        }
    } else {
        folder
            .map(PathBuf::from)
            .context("Either folder or git-url must be provided")
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    #[test]
    fn test_get_folder_path_local() {
        let temp_dir = TempDir::new().unwrap();
        let folder_path = temp_dir.path().to_str().unwrap();
        let cache_dir = PathBuf::from("/tmp/cache");
        
        let result = get_folder_path(Some(folder_path), None, &cache_dir, false).unwrap();
        assert_eq!(result, PathBuf::from(folder_path));
    }

    #[test]
    fn test_get_folder_path_no_args() {
        let cache_dir = PathBuf::from("/tmp/cache");
        let result = get_folder_path(None, None, &cache_dir, false);
        assert!(result.is_err());
    }
}

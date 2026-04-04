use anyhow::{Context, Result};
use git2::Repository;
use std::path::{Path, PathBuf};
use url::Url;

/// Get the local cache path for a git repository
pub fn get_local_cache_path(git_url: &str, cache_dir: &Path) -> Result<PathBuf> {
    // Parse the git URL to extract owner and name
    let (owner, name) = parse_git_url(git_url)?;
    
    Ok(cache_dir.join("git").join(owner).join(name))
}

/// Parse a git URL to extract owner and repository name
fn parse_git_url(git_url: &str) -> Result<(String, String)> {
    // Try to parse as URL first
    if let Ok(url) = Url::parse(git_url) {
        // Handle HTTPS URLs
        if url.scheme() == "https" || url.scheme() == "http" {
            let path = url.path().trim_start_matches('/').trim_end_matches(".git");
            let parts: Vec<&str> = path.split('/').collect();
            if parts.len() >= 2 {
                return Ok((parts[0].to_string(), parts[1].to_string()));
            }
        }
    }
    
    // Handle SSH URLs (git@github.com:owner/repo.git)
    if git_url.starts_with("git@") {
        if let Some(colon_pos) = git_url.find(':') {
            let path = &git_url[colon_pos + 1..].trim_end_matches(".git");
            let parts: Vec<&str> = path.split('/').collect();
            if parts.len() >= 2 {
                return Ok((parts[0].to_string(), parts[1].to_string()));
            }
        }
    }
    
    anyhow::bail!("Cannot extract user/repo from git URL: {}", git_url)
}

/// Clone or update a git repository at the specified local path
pub fn clone_or_update_repo(
    git_url: &str,
    local_path: &Path,
    auto_pull: bool,
) -> Result<()> {
    if local_path.exists() {
        if auto_pull {
            // Pull latest changes
            let repo = Repository::open(local_path)
                .context("Failed to open existing repository")?;
            
            // Fetch from origin
            let mut remote = repo.find_remote("origin")
                .context("Failed to find remote 'origin'")?;
            remote.fetch(&["main", "master"], None, None)
                .or_else(|_| remote.fetch(&["HEAD"], None, None))
                .context("Failed to fetch from remote")?;
            
            // Fast-forward merge
            let fetch_head = repo.find_reference("FETCH_HEAD")
                .context("Failed to find FETCH_HEAD")?;
            let fetch_commit = repo.reference_to_annotated_commit(&fetch_head)
                .context("Failed to get fetch commit")?;
            
            let analysis = repo.merge_analysis(&[&fetch_commit])
                .context("Failed to analyze merge")?;
            
            if analysis.0.is_up_to_date() {
                // Already up to date
            } else if analysis.0.is_fast_forward() {
                // Fast-forward merge
                let refname = "refs/heads/main";
                let mut reference = repo.find_reference(refname)
                    .or_else(|_| repo.find_reference("refs/heads/master"))
                    .context("Failed to find branch reference")?;
                reference.set_target(fetch_commit.id(), "Fast-forward")
                    .context("Failed to set target")?;
                repo.set_head(reference.name().unwrap())
                    .context("Failed to set HEAD")?;
                repo.checkout_head(Some(git2::build::CheckoutBuilder::default().force()))
                    .context("Failed to checkout HEAD")?;
            }
        }
    } else {
        // Clone the repository
        std::fs::create_dir_all(local_path.parent().unwrap())
            .context("Failed to create cache directory")?;
        
        let mut builder = git2::build::RepoBuilder::new();
        builder.fetch_options({
            let mut fo = git2::FetchOptions::new();
            fo.depth(1); // Shallow clone
            fo
        });
        
        builder.clone(git_url, local_path)
            .context(format!("Failed to clone repository from {}", git_url))?;
    }
    
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_https_git_url() {
        let url = "https://github.com/owner/repo.git";
        let (owner, name) = parse_git_url(url).unwrap();
        assert_eq!(owner, "owner");
        assert_eq!(name, "repo");
    }

    #[test]
    fn test_parse_ssh_git_url() {
        let url = "git@github.com:owner/repo.git";
        let (owner, name) = parse_git_url(url).unwrap();
        assert_eq!(owner, "owner");
        assert_eq!(name, "repo");
    }
}

use crate::model::{Argument, PromptData};
use anyhow::{Context, Result};
use serde::Deserialize;
use std::path::{Path, PathBuf};
use walkdir::WalkDir;

#[derive(Debug, Deserialize)]
struct Frontmatter {
    #[serde(default)]
    name: Option<String>,
    #[serde(default)]
    title: Option<String>,
    #[serde(default)]
    description: Option<String>,
    #[serde(default)]
    arguments: Vec<Argument>,
}

/// Parse a markdown file with YAML frontmatter
fn parse_markdown_file(
    md_file: &Path,
    folder: &Path,
    content: &str,
    skip_frontmatter: bool,
) -> Result<PromptData> {
    let file_stem = md_file
        .file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or("unnamed");
    
    let relative_path = md_file
        .strip_prefix(folder)
        .unwrap_or(md_file)
        .display()
        .to_string();
    
    let default_description = format!("Prompt from {}", relative_path);
    
    if skip_frontmatter {
        // Skip frontmatter processing, use file content as-is
        return Ok(PromptData {
            name: file_stem.to_string(),
            title: file_stem.to_string(),
            description: default_description,
            arguments: Vec::new(),
            content: content.to_string(),
        });
    }
    
    // Parse frontmatter using yaml-front-matter crate
    let (frontmatter, content_text) = if content.starts_with("---") {
        // Find the end of frontmatter
        let lines: Vec<&str> = content.lines().collect();
        if lines.len() > 1 {
            // Find second ---
            if let Some(end_idx) = lines[1..].iter().position(|&line| line == "---") {
                let yaml_content = lines[1..=end_idx].join("\n");
                let content_start = end_idx + 2;
                let content_text = if content_start < lines.len() {
                    lines[content_start..].join("\n")
                } else {
                    String::new()
                };
                
                match serde_yaml::from_str::<Frontmatter>(&yaml_content) {
                    Ok(fm) => (Some(fm), content_text),
                    Err(e) => {
                        eprintln!("Warning: failed to parse frontmatter in {}: {}", md_file.display(), e);
                        (None, content.to_string())
                    }
                }
            } else {
                (None, content.to_string())
            }
        } else {
            (None, content.to_string())
        }
    } else {
        (None, content.to_string())
    };
    
    let (name, title, description, arguments) = if let Some(fm) = frontmatter {
        let name = fm.name.as_deref().unwrap_or(file_stem);
        let title = fm.title.as_deref().unwrap_or(file_stem);
        let description = fm.description.as_deref().unwrap_or(&default_description);
        (
            name.to_string(),
            title.to_string(),
            description.to_string(),
            fm.arguments,
        )
    } else {
        (
            file_stem.to_string(),
            file_stem.to_string(),
            default_description,
            Vec::new(),
        )
    };
    
    Ok(PromptData {
        name,
        title,
        description,
        arguments,
        content: content_text,
    })
}

/// Scan folder recursively for markdown files
pub fn scan_markdown_files(
    folder: &Path,
    skip_frontmatter: bool,
) -> Result<Vec<PromptData>> {
    let folder = if folder.starts_with("~") {
        let home = dirs::home_dir().context("Could not determine home directory")?;
        let path_str = folder.to_string_lossy();
        let without_tilde = path_str.strip_prefix("~/").unwrap_or(&path_str);
        home.join(without_tilde)
    } else {
        folder.to_path_buf()
    };
    
    if !folder.exists() || !folder.is_dir() {
        eprintln!(
            "Warning: folder path '{}' does not exist or is not a directory",
            folder.display()
        );
        return Ok(Vec::new());
    }
    
    let mut prompts = Vec::new();
    
    for entry in WalkDir::new(&folder)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| e.file_type().is_file())
        .filter(|e| {
            e.path()
                .extension()
                .and_then(|s| s.to_str())
                .map(|s| s.eq_ignore_ascii_case("md"))
                .unwrap_or(false)
        })
    {
        let path = entry.path();
        match std::fs::read_to_string(path) {
            Ok(content) => {
                match parse_markdown_file(path, &folder, &content, skip_frontmatter) {
                    Ok(prompt_data) => prompts.push(prompt_data),
                    Err(e) => {
                        eprintln!("Warning: failed to process {}: {}", path.display(), e);
                    }
                }
            }
            Err(e) => {
                eprintln!("Warning: failed to read {}: {}", path.display(), e);
            }
        }
    }
    
    Ok(prompts)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_parse_markdown_without_frontmatter() {
        let content = "Hello world!";
        let temp_dir = TempDir::new().unwrap();
        let file_path = temp_dir.path().join("test.md");
        
        let result = parse_markdown_file(&file_path, temp_dir.path(), content, false).unwrap();
        assert_eq!(result.name, "test");
        assert_eq!(result.content, "Hello world!");
    }

    #[test]
    fn test_parse_markdown_with_frontmatter() {
        let content = r#"---
name: greeting
title: Greeting Prompt
description: A simple greeting
arguments:
  - name: user
    description: User name
---
Hello {user}!"#;
        
        let temp_dir = TempDir::new().unwrap();
        let file_path = temp_dir.path().join("test.md");
        
        let result = parse_markdown_file(&file_path, temp_dir.path(), content, false).unwrap();
        assert_eq!(result.name, "greeting");
        assert_eq!(result.title, "Greeting Prompt");
        assert_eq!(result.content.trim(), "Hello {user}!");
        assert_eq!(result.arguments.len(), 1);
        assert_eq!(result.arguments[0].name, "user");
    }
}

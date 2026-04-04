use clap::{Parser, ValueEnum};
use std::path::PathBuf;

#[derive(Debug, Clone, Copy, ValueEnum)]
pub enum FormatterType {
    Brace,
    Dollar,
}

#[derive(Parser, Debug)]
#[command(name = "shinkuro")]
#[command(about = "Shinkuro - Universal prompt loader MCP server", long_about = None)]
pub struct Cli {
    /// Path to local folder containing markdown files, or subfolder within git repo
    #[arg(long, env = "FOLDER")]
    pub folder: Option<String>,

    /// Git repository URL (supports GitHub, GitLab, SSH, HTTPS with credentials)
    #[arg(long, env = "GIT_URL")]
    pub git_url: Option<String>,

    /// Directory to cache remote repositories
    #[arg(long, env = "CACHE_DIR", default_value = "~/.shinkuro/remote")]
    pub cache_dir: PathBuf,

    /// Whether to refresh local cache on startup
    #[arg(long, env = "AUTO_PULL")]
    pub auto_pull: bool,

    /// Template variable format
    #[arg(long, env = "VARIABLE_FORMAT", value_enum, default_value = "brace")]
    pub variable_format: FormatterType,

    /// Auto-discover template variables as required arguments
    #[arg(long, env = "AUTO_DISCOVER_ARGS")]
    pub auto_discover_args: bool,

    /// Skip frontmatter processing and use raw markdown content
    #[arg(long, env = "SKIP_FRONTMATTER")]
    pub skip_frontmatter: bool,

    /// Show version and exit
    #[arg(long)]
    pub version: bool,
}

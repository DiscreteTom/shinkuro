mod cli;
mod file;
mod formatters;
mod git;
mod loader;
mod mcp;
mod model;

use clap::Parser;
use cli::Cli;
use std::process;

const VERSION: &str = env!("CARGO_PKG_VERSION");

fn main() {
    let cli = Cli::parse();
    
    if cli.version {
        println!("Shinkuro Version: {}", VERSION);
        return;
    }
    
    if let Err(e) = run(cli) {
        eprintln!("Error: {}", e);
        process::exit(1);
    }
}

fn run(cli: Cli) -> anyhow::Result<()> {
    // Get the folder path (either local or from git)
    let folder_path = loader::get_folder_path(
        cli.folder.as_deref(),
        cli.git_url.as_deref(),
        &cli.cache_dir,
        cli.auto_pull,
    )?;
    
    // Get the formatter
    let formatter = formatters::get_formatter(cli.variable_format);
    
    // Scan markdown files and load prompts
    let prompts = file::scan_markdown_files(
        &folder_path,
        cli.skip_frontmatter,
    )?;
    
    // Create MCP server with prompts
    let runtime = tokio::runtime::Runtime::new()?;
    runtime.block_on(async {
        mcp::run_server(prompts, formatter, cli.auto_discover_args).await
    })
}

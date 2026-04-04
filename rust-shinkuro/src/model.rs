use serde::{Deserialize, Serialize};

/// Template argument for prompt substitution
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Argument {
    /// Parameter name for template substitution
    pub name: String,
    /// Human-readable description of the parameter
    #[serde(default)]
    pub description: String,
    /// Default value if parameter not provided
    #[serde(default)]
    pub default: Option<String>,
}

/// Complete prompt data loaded from markdown file
#[derive(Debug, Clone)]
pub struct PromptData {
    /// Unique identifier for the prompt
    pub name: String,
    /// Display title for the prompt
    pub title: String,
    /// Brief description of prompt purpose
    pub description: String,
    /// Template arguments this prompt accepts
    pub arguments: Vec<Argument>,
    /// Template content for variable substitution
    pub content: String,
}

use crate::cli::FormatterType;
use regex::Regex;
use std::collections::{HashMap, HashSet};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum FormatterError {
    #[error("Invalid variable name: {0}")]
    InvalidVariableName(String),
    #[error("Invalid template syntax: {0}")]
    InvalidSyntax(String),
}

/// Validate that a variable name is a valid identifier
pub fn validate_variable_name(name: &str) -> bool {
    let re = Regex::new(r"^[a-zA-Z_][a-zA-Z0-9_]*$").unwrap();
    re.is_match(name)
}

/// Trait for template formatters
pub trait Formatter: Send + Sync {
    /// Extract argument names from content
    fn extract_arguments(&self, content: &str) -> Result<HashSet<String>, FormatterError>;
    
    /// Format content with variables
    fn format(&self, content: &str, variables: &HashMap<String, String>) -> String;
}

/// Formatter for {var} syntax
pub struct BraceFormatter;

impl BraceFormatter {
    pub fn new() -> Self {
        Self
    }
}

impl Formatter for BraceFormatter {
    fn extract_arguments(&self, content: &str) -> Result<HashSet<String>, FormatterError> {
        let re = Regex::new(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}").unwrap();
        let mut arguments = HashSet::new();
        
        for cap in re.captures_iter(content) {
            let var_name = &cap[1];
            if !validate_variable_name(var_name) {
                return Err(FormatterError::InvalidVariableName(var_name.to_string()));
            }
            arguments.insert(var_name.to_string());
        }
        
        Ok(arguments)
    }
    
    fn format(&self, content: &str, variables: &HashMap<String, String>) -> String {
        let re = Regex::new(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}").unwrap();
        re.replace_all(content, |caps: &regex::Captures| {
            let var_name = &caps[1];
            variables.get(var_name)
                .map(|s| s.as_str())
                .unwrap_or(&caps[0])
        }).to_string()
    }
}

/// Formatter for $var syntax
pub struct DollarFormatter;

impl DollarFormatter {
    pub fn new() -> Self {
        Self
    }
}

impl Formatter for DollarFormatter {
    fn extract_arguments(&self, content: &str) -> Result<HashSet<String>, FormatterError> {
        // Match $identifier pattern
        let re = Regex::new(r"\$([a-zA-Z_][a-zA-Z0-9_]*)").unwrap();
        let mut arguments = HashSet::new();
        
        for cap in re.captures_iter(content) {
            let var_name = &cap[1];
            if !validate_variable_name(var_name) {
                return Err(FormatterError::InvalidVariableName(var_name.to_string()));
            }
            arguments.insert(var_name.to_string());
        }
        
        Ok(arguments)
    }
    
    fn format(&self, content: &str, variables: &HashMap<String, String>) -> String {
        let re = Regex::new(r"\$([a-zA-Z_][a-zA-Z0-9_]*)").unwrap();
        re.replace_all(content, |caps: &regex::Captures| {
            let var_name = &caps[1];
            variables.get(var_name)
                .map(|s| s.as_str())
                .unwrap_or(&caps[0])
        }).to_string()
    }
}

/// Get formatter by type
pub fn get_formatter(formatter_type: FormatterType) -> Box<dyn Formatter> {
    match formatter_type {
        FormatterType::Brace => Box::new(BraceFormatter::new()),
        FormatterType::Dollar => Box::new(DollarFormatter::new()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_brace_formatter() {
        let formatter = BraceFormatter::new();
        let content = "Hello {name}, welcome to {project}!";
        
        // Test extraction
        let args = formatter.extract_arguments(content).unwrap();
        assert_eq!(args.len(), 2);
        assert!(args.contains("name"));
        assert!(args.contains("project"));
        
        // Test formatting
        let mut vars = HashMap::new();
        vars.insert("name".to_string(), "Alice".to_string());
        vars.insert("project".to_string(), "Rust".to_string());
        let result = formatter.format(content, &vars);
        assert_eq!(result, "Hello Alice, welcome to Rust!");
    }

    #[test]
    fn test_dollar_formatter() {
        let formatter = DollarFormatter::new();
        let content = "Hello $name, welcome to $project!";
        
        // Test extraction
        let args = formatter.extract_arguments(content).unwrap();
        assert_eq!(args.len(), 2);
        assert!(args.contains("name"));
        assert!(args.contains("project"));
        
        // Test formatting
        let mut vars = HashMap::new();
        vars.insert("name".to_string(), "Bob".to_string());
        vars.insert("project".to_string(), "Python".to_string());
        let result = formatter.format(content, &vars);
        assert_eq!(result, "Hello Bob, welcome to Python!");
    }
}

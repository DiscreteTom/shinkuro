use crate::formatters::{validate_variable_name, Formatter};
use crate::model::PromptData;
use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};
use std::io::{self, BufRead, Write};

/// MCP Protocol message types
#[derive(Debug, Serialize, Deserialize)]
#[serde(tag = "method")]
enum Request {
    #[serde(rename = "initialize")]
    Initialize { id: serde_json::Value, params: InitializeParams },
    #[serde(rename = "prompts/list")]
    PromptsList { id: serde_json::Value },
    #[serde(rename = "prompts/get")]
    PromptsGet { id: serde_json::Value, params: PromptsGetParams },
    #[serde(rename = "notifications/initialized")]
    NotificationsInitialized,
}

#[derive(Debug, Serialize, Deserialize)]
struct InitializeParams {
    #[serde(rename = "protocolVersion")]
    protocol_version: String,
    capabilities: serde_json::Value,
    #[serde(rename = "clientInfo")]
    client_info: ClientInfo,
}

#[derive(Debug, Serialize, Deserialize)]
struct ClientInfo {
    name: String,
    version: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct PromptsGetParams {
    name: String,
    #[serde(default)]
    arguments: Option<HashMap<String, String>>,
}

#[derive(Debug, Serialize)]
struct Response {
    jsonrpc: String,
    id: serde_json::Value,
    result: serde_json::Value,
}

#[derive(Debug, Serialize)]
struct ErrorResponse {
    jsonrpc: String,
    id: serde_json::Value,
    error: ErrorDetails,
}

#[derive(Debug, Serialize)]
struct ErrorDetails {
    code: i32,
    message: String,
}

#[derive(Debug, Serialize)]
struct InitializeResult {
    #[serde(rename = "protocolVersion")]
    protocol_version: String,
    capabilities: Capabilities,
    #[serde(rename = "serverInfo")]
    server_info: ServerInfo,
}

#[derive(Debug, Serialize)]
struct Capabilities {
    prompts: PromptsCapability,
}

#[derive(Debug, Serialize)]
struct PromptsCapability {
    #[serde(rename = "listChanged")]
    list_changed: bool,
}

#[derive(Debug, Serialize)]
struct ServerInfo {
    name: String,
    version: String,
}

#[derive(Debug, Serialize)]
struct PromptsListResult {
    prompts: Vec<PromptInfo>,
}

#[derive(Debug, Serialize)]
struct PromptInfo {
    name: String,
    description: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    arguments: Option<Vec<PromptArgument>>,
}

#[derive(Debug, Serialize)]
struct PromptArgument {
    name: String,
    description: String,
    required: bool,
}

#[derive(Debug, Serialize)]
struct PromptsGetResult {
    description: String,
    messages: Vec<PromptMessage>,
}

#[derive(Debug, Serialize)]
struct PromptMessage {
    role: String,
    content: MessageContent,
}

#[derive(Debug, Serialize)]
struct MessageContent {
    #[serde(rename = "type")]
    content_type: String,
    text: String,
}

/// Prompt with rendering capability
struct MarkdownPrompt {
    name: String,
    title: String,
    description: String,
    arguments: Vec<crate::model::Argument>,
    content: String,
}

impl MarkdownPrompt {
    fn new(
        prompt_data: PromptData,
        formatter: &dyn Formatter,
        auto_discover_args: bool,
    ) -> Result<Self> {
        if auto_discover_args {
            // Auto-discover arguments from template variables
            if !prompt_data.arguments.is_empty() {
                anyhow::bail!("prompt_data.arguments must be empty when auto_discover_args is enabled");
            }
            let discovered_args = formatter.extract_arguments(&prompt_data.content)?;
            let mut arguments = Vec::new();
            for arg in discovered_args.iter() {
                arguments.push(crate::model::Argument {
                    name: arg.clone(),
                    description: String::new(),
                    default: None,
                });
            }
            arguments.sort_by(|a, b| a.name.cmp(&b.name));
            
            Ok(Self {
                name: prompt_data.name,
                title: prompt_data.title,
                description: prompt_data.description,
                arguments,
                content: prompt_data.content,
            })
        } else {
            // Validate arguments
            for arg in &prompt_data.arguments {
                if !validate_variable_name(&arg.name) {
                    anyhow::bail!("Argument name '{}' contains invalid characters", arg.name);
                }
            }
            
            // Validate content and get discovered arguments
            let discovered_args = formatter.extract_arguments(&prompt_data.content)?;
            let provided_args: HashSet<String> = prompt_data
                .arguments
                .iter()
                .map(|a| a.name.clone())
                .collect();
            
            if discovered_args != provided_args {
                anyhow::bail!(
                    "Content arguments {:?} don't match provided arguments {:?}",
                    discovered_args,
                    provided_args
                );
            }
            
            Ok(Self {
                name: prompt_data.name,
                title: prompt_data.title,
                description: prompt_data.description,
                arguments: prompt_data.arguments,
                content: prompt_data.content,
            })
        }
    }
    
    fn render(
        &self,
        arguments: Option<HashMap<String, String>>,
        formatter: &dyn Formatter,
    ) -> Result<String> {
        // Validate required arguments
        let required: HashSet<String> = self
            .arguments
            .iter()
            .filter(|a| a.default.is_none())
            .map(|a| a.name.clone())
            .collect();
        
        let provided: HashSet<String> = arguments
            .as_ref()
            .map(|m| m.keys().cloned().collect())
            .unwrap_or_default();
        
        let missing: Vec<_> = required.difference(&provided).collect();
        if !missing.is_empty() {
            anyhow::bail!("Missing required arguments: {:?}", missing);
        }
        
        // Merge provided arguments with defaults
        let mut render_args = HashMap::new();
        for arg in &self.arguments {
            if let Some(default) = &arg.default {
                render_args.insert(arg.name.clone(), default.clone());
            }
        }
        if let Some(args) = arguments {
            render_args.extend(args);
        }
        
        // Perform variable substitution using formatter
        Ok(formatter.format(&self.content, &render_args))
    }
    
    fn to_prompt_info(&self) -> PromptInfo {
        let arguments = if self.arguments.is_empty() {
            None
        } else {
            Some(
                self.arguments
                    .iter()
                    .map(|a| PromptArgument {
                        name: a.name.clone(),
                        description: a.description.clone(),
                        required: a.default.is_none(),
                    })
                    .collect(),
            )
        };
        
        PromptInfo {
            name: self.name.clone(),
            description: self.description.clone(),
            arguments,
        }
    }
}

/// Run the MCP server
pub async fn run_server(
    prompts: Vec<PromptData>,
    formatter: Box<dyn Formatter>,
    auto_discover_args: bool,
) -> Result<()> {
    // Convert PromptData to MarkdownPrompt
    let mut markdown_prompts = Vec::new();
    for prompt_data in prompts {
        match MarkdownPrompt::new(prompt_data, formatter.as_ref(), auto_discover_args) {
            Ok(prompt) => markdown_prompts.push(prompt),
            Err(e) => {
                eprintln!("Warning: failed to create prompt: {}", e);
            }
        }
    }
    
    let stdin = io::stdin();
    let mut stdout = io::stdout();
    let reader = stdin.lock();
    
    for line in reader.lines() {
        let line = line?;
        if line.trim().is_empty() {
            continue;
        }
        
        // Parse the JSON-RPC request
        let request: serde_json::Value = match serde_json::from_str(&line) {
            Ok(req) => req,
            Err(e) => {
                eprintln!("Warning: failed to parse request: {}", e);
                continue;
            }
        };
        
        let response = handle_request(&request, &markdown_prompts, formatter.as_ref())?;
        
        if let Some(response_json) = response {
            let response_str = serde_json::to_string(&response_json)?;
            writeln!(stdout, "{}", response_str)?;
            stdout.flush()?;
        }
    }
    
    Ok(())
}

fn handle_request(
    request: &serde_json::Value,
    prompts: &[MarkdownPrompt],
    formatter: &dyn Formatter,
) -> Result<Option<serde_json::Value>> {
    let method = request.get("method").and_then(|m| m.as_str());
    let id = request.get("id").cloned();
    
    match method {
        Some("initialize") => {
            let result = InitializeResult {
                protocol_version: "2024-11-05".to_string(),
                capabilities: Capabilities {
                    prompts: PromptsCapability {
                        list_changed: false,
                    },
                },
                server_info: ServerInfo {
                    name: "shinkuro".to_string(),
                    version: env!("CARGO_PKG_VERSION").to_string(),
                },
            };
            
            Ok(Some(serde_json::json!({
                "jsonrpc": "2.0",
                "id": id,
                "result": result,
            })))
        }
        Some("notifications/initialized") => {
            // No response needed for notifications
            Ok(None)
        }
        Some("prompts/list") => {
            let prompts_list: Vec<PromptInfo> = prompts
                .iter()
                .map(|p| p.to_prompt_info())
                .collect();
            
            let result = PromptsListResult {
                prompts: prompts_list,
            };
            
            Ok(Some(serde_json::json!({
                "jsonrpc": "2.0",
                "id": id,
                "result": result,
            })))
        }
        Some("prompts/get") => {
            let params = request.get("params");
            let name = params
                .and_then(|p| p.get("name"))
                .and_then(|n| n.as_str())
                .ok_or_else(|| anyhow::anyhow!("Missing prompt name"))?;
            
            let arguments = params
                .and_then(|p| p.get("arguments"))
                .and_then(|a| serde_json::from_value(a.clone()).ok());
            
            // Find the prompt
            let prompt = prompts
                .iter()
                .find(|p| p.name == name)
                .ok_or_else(|| anyhow::anyhow!("Prompt not found: {}", name))?;
            
            // Render the prompt
            match prompt.render(arguments, formatter) {
                Ok(content) => {
                    let result = PromptsGetResult {
                        description: prompt.description.clone(),
                        messages: vec![PromptMessage {
                            role: "user".to_string(),
                            content: MessageContent {
                                content_type: "text".to_string(),
                                text: content,
                            },
                        }],
                    };
                    
                    Ok(Some(serde_json::json!({
                        "jsonrpc": "2.0",
                        "id": id,
                        "result": result,
                    })))
                }
                Err(e) => {
                    let error = ErrorDetails {
                        code: -32602,
                        message: format!("Failed to render prompt: {}", e),
                    };
                    
                    Ok(Some(serde_json::json!({
                        "jsonrpc": "2.0",
                        "id": id,
                        "error": error,
                    })))
                }
            }
        }
        _ => {
            let error = ErrorDetails {
                code: -32601,
                message: format!("Method not found: {:?}", method),
            };
            
            Ok(Some(serde_json::json!({
                "jsonrpc": "2.0",
                "id": id,
                "error": error,
            })))
        }
    }
}

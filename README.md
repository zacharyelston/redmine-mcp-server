# Redmine MCP Server

A Model Context Protocol (MCP) server that enables AI assistants to interact with Redmine for focused and transparent project management.

## Overview

This MCP server provides a bridge between AI assistants and Redmine, allowing the AI to:

- Create and update issues with proper categorization
- Manage wiki pages and documentation
- Track project status and progress
- Follow defined processes for consistency

By using this MCP server, you can ensure that AI work remains focused, well-documented, and fully transparent to human team members.

## Features

### Resource Capabilities
- **Issues**: Access to Redmine issues with filtering and search
- **Projects**: Access to project data, categories, and statuses
- **Wiki**: Access to wiki pages for documentation

### Tool Capabilities
- **create_issue**: Create new issues with proper categorization
- **update_issue**: Update existing issues with status changes and notes
- **create_wiki**: Create or update wiki pages for documentation
- **get_project_status**: Get project status summaries and statistics

### Prompt Capabilities
- **issue_template**: Template for creating well-structured issues
- **wiki_template**: Template for creating well-structured wiki pages

## Requirements

- Python 3.9+
- Flask
- Redmine instance with API access
- Claude Desktop or other MCP-compatible AI assistant

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/redmine-mcp-server.git
   cd redmine-mcp-server
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the server:
   ```
   cp config.yaml.example config.yaml
   # Edit config.yaml with your Redmine URL and API key
   ```

## Usage

### Running the server

Start the server with:

```
python main.py
```

The server runs on port 5000 by default.

### Docker deployment

Build and run the Docker container:

```
docker build -t redmine-mcp-server .
docker run -d -p 5000:5000 -e REDMINE_API_KEY=your_api_key -e REDMINE_URL=http://localhost:3000 redmine-mcp-server
```

### Configuring Claude Desktop

Add the following to your Claude Desktop MCP configuration:

```json
{
  "mcps": {
    "redmine": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "REDMINE_API_KEY",
        "-e",
        "REDMINE_URL",
        "redmine-mcp-server:latest"
      ],
      "environment": {
        "REDMINE_API_KEY": "your_redmine_api_key",
        "REDMINE_URL": "http://localhost:3000"
      }
    }
  }
}
```

## API Reference

### MCP Endpoints

- `GET /mcp`: Returns MCP capabilities
- `GET /mcp/health`: Returns health status

### Resource Endpoints

- `GET /mcp/resources/issues`: Returns issues as resources
- `GET /mcp/resources/projects`: Returns project data
- `GET /mcp/resources/wiki`: Returns wiki pages

### Tool Endpoints

- `POST /mcp/tools/create_issue`: Creates a new issue
- `POST /mcp/tools/update_issue`: Updates an existing issue
- `POST /mcp/tools/create_wiki`: Creates or updates a wiki page
- `POST /mcp/tools/get_project_status`: Gets project status and statistics

### Prompt Endpoints

- `GET /mcp/prompts/issue_template`: Returns template for creating issues
- `GET /mcp/prompts/wiki_template`: Returns template for creating wiki pages

## Configuration Options

The server can be configured using a `config.yaml` file or environment variables:

| Option | Environment Variable | Description | Default |
|--------|----------------------|-------------|---------|
| redmine_url | REDMINE_URL | URL of the Redmine instance | http://localhost:3000 |
| redmine_api_key | REDMINE_API_KEY | API key for Redmine authentication | None |
| server_port | SERVER_PORT | Port for the MCP server | 5000 |
| log_level | LOG_LEVEL | Logging level (INFO, DEBUG, etc.) | INFO |
| project_id | PROJECT_ID | Default Redmine project ID | 1 |
| default_category_id | DEFAULT_CATEGORY_ID | Default category ID for issues | 3 |
| default_tracker_id | DEFAULT_TRACKER_ID | Default tracker ID for issues | 2 |

## Process Benefits

Using this MCP server provides several benefits for AI-assisted project management:

1. **Structured Documentation**: All AI work is automatically documented in Redmine
2. **Clear Processes**: AI tasks follow predefined workflows and categories
3. **Transparency**: All AI actions are logged and traceable
4. **Collaboration**: Human team members can easily review and contribute to AI work
5. **Progress Tracking**: Project managers can track AI task progress through Redmine

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

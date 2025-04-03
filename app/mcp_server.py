"""
Model Context Protocol (MCP) Server for Redmine integration
Provides MCP capabilities for AI assistants to interact with Redmine
"""

import json
import logging
import os
from flask import Flask, request, jsonify

from app.redmine_api import RedmineAPI
from app.config import load_config, setup_logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

# Load configuration
config = load_config()

# Initialize Flask app
app = Flask(__name__)

# Initialize Redmine API client
redmine = RedmineAPI(config.get('redmine_url'), config.get('redmine_api_key'))

@app.route('/mcp', methods=['GET'])
def mcp_capabilities():
    """
    Standard MCP endpoint that returns the capabilities of this extension
    """
    return jsonify({
        "id": "redmine-ai-assistant-mcp",
        "name": "Redmine AI Assistant MCP",
        "description": "MCP server for AI-assisted Redmine project management",
        "version": "0.1.0",
        "publisher": "Redmine MCP Server",
        "contact": "https://github.com/yourusername/redmine-mcp-server",
        "capabilities": [
            {
                "type": "resource",
                "name": "issues",
                "description": "Access to Redmine issues",
                "endpoint": "/mcp/resources/issues"
            },
            {
                "type": "resource",
                "name": "projects",
                "description": "Access to Redmine projects",
                "endpoint": "/mcp/resources/projects"
            },
            {
                "type": "resource",
                "name": "wiki",
                "description": "Access to Redmine wiki pages",
                "endpoint": "/mcp/resources/wiki"
            },
            {
                "type": "tool",
                "name": "create_issue",
                "description": "Create a new issue in Redmine",
                "endpoint": "/mcp/tools/create_issue"
            },
            {
                "type": "tool",
                "name": "update_issue",
                "description": "Update an existing issue in Redmine",
                "endpoint": "/mcp/tools/update_issue"
            },
            {
                "type": "tool",
                "name": "create_wiki",
                "description": "Create or update a wiki page in Redmine",
                "endpoint": "/mcp/tools/create_wiki"
            },
            {
                "type": "tool",
                "name": "get_project_status",
                "description": "Get current project status and summary",
                "endpoint": "/mcp/tools/get_project_status"
            },
            {
                "type": "prompt",
                "name": "issue_template",
                "description": "Template for creating well-structured issues",
                "endpoint": "/mcp/prompts/issue_template"
            },
            {
                "type": "prompt",
                "name": "wiki_template",
                "description": "Template for creating well-structured wiki pages",
                "endpoint": "/mcp/prompts/wiki_template"
            }
        ]
    })

@app.route('/mcp/health', methods=['GET'])
def mcp_health():
    """
    Health check endpoint for the MCP server
    """
    try:
        # Check Redmine API connection
        project_id = config.get('project_id', 1)
        redmine.get_project(project_id)
        
        return jsonify({
            "status": "healthy",
            "message": "Redmine MCP Server is running and connected to Redmine",
            "redmine_url": config.get('redmine_url')
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "message": f"Failed to connect to Redmine: {str(e)}",
            "redmine_url": config.get('redmine_url')
        }), 500

# Register resource endpoints
@app.route('/mcp/resources/issues', methods=['GET'])
def get_issues_resource():
    """Get issues resource"""
    try:
        return resources.get_issues_resource(redmine, config)
    except Exception as e:
        logger.error(f"Error in issues resource: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/resources/projects', methods=['GET'])
def get_projects_resource():
    """Get projects resource"""
    try:
        return resources.get_projects_resource(redmine, config)
    except Exception as e:
        logger.error(f"Error in projects resource: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/resources/wiki', methods=['GET'])
def get_wiki_resource():
    """Get wiki resource"""
    try:
        return resources.get_wiki_resource(redmine, config)
    except Exception as e:
        logger.error(f"Error in wiki resource: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Register tool endpoints
@app.route('/mcp/tools/create_issue', methods=['POST'])
def create_issue_tool():
    """Create issue tool"""
    try:
        return tools.create_issue_tool(redmine, request.json, config)
    except Exception as e:
        logger.error(f"Error in create_issue tool: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/tools/update_issue', methods=['POST'])
def update_issue_tool():
    """Update issue tool"""
    try:
        return tools.update_issue_tool(redmine, request.json, config)
    except Exception as e:
        logger.error(f"Error in update_issue tool: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/tools/create_wiki', methods=['POST'])
def create_wiki_tool():
    """Create wiki tool"""
    try:
        return tools.create_wiki_tool(redmine, request.json, config)
    except Exception as e:
        logger.error(f"Error in create_wiki tool: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/tools/get_project_status', methods=['POST'])
def get_project_status_tool():
    """Get project status tool"""
    try:
        return tools.get_project_status_tool(redmine, request.json, config)
    except Exception as e:
        logger.error(f"Error in get_project_status tool: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Register prompt endpoints
@app.route('/mcp/prompts/issue_template', methods=['GET'])
def issue_template_prompt():
    """Issue template prompt"""
    with open(os.path.join(os.path.dirname(__file__), 'prompts/issue_template.txt'), 'r') as f:
        template = f.read()
    
    return jsonify({
        "prompt": template,
        "variables": ["title", "description", "category", "priority"]
    })

@app.route('/mcp/prompts/wiki_template', methods=['GET'])
def wiki_template_prompt():
    """Wiki template prompt"""
    with open(os.path.join(os.path.dirname(__file__), 'prompts/wiki_template.txt'), 'r') as f:
        template = f.read()
    
    return jsonify({
        "prompt": template,
        "variables": ["title", "content", "section_headings"]
    })

def run_server():
    """Run the MCP server"""
    port = int(config.get('server_port', 5050))
    app.run(host='0.0.0.0', port=port)

# Fix missing imports
import app.resources as resources
import app.tools as tools

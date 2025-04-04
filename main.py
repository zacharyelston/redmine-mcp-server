"""
Main entry point for the Redmine MCP Server

This server provides Model Context Protocol (MCP) capabilities for AI assistants
to interact with Redmine project management system
"""

import logging
import os
import sys
import signal
import json
import time

from app.mcp_server import app, run_server
from app.config import setup_logging, load_config

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

def handle_shutdown(signum, frame):
    """Handle graceful shutdown"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    # If needed, perform cleanup here
    logger.info("Shutdown complete")
    sys.exit(0)

def simulate_mcp_response():
    """Simulate MCP response for testing"""
    # This function would respond directly to Claude's MCP client
    logger.info("Simulating response to MCP client")
    
    # Print to stdout (should be captured by the MCP client)
    response = {
        "jsonrpc": "2.0",
        "id": 0,
        "result": {
            "capabilities": {
                "executeCommand": True,
                "searchRedmine": True,
                "createIssue": True,
                "updateIssue": True
            },
            "name": "redmine-mcp-server",
            "version": "0.1.0"
        }
    }
    
    # If in special debug mode, print to stderr instead
    if os.environ.get('MCP_DEBUG', '').lower() == 'true':
        print(f"MCP RESPONSE: {json.dumps(response)}", file=sys.stderr)
    else:
        print(json.dumps(response))
        sys.stdout.flush()

if __name__ == '__main__':
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)
    
    logger.info("Starting Redmine MCP Server")
    
    # Check for Claude desktop environment
    in_claude_desktop = 'CLAUDE_DESKTOP' in os.environ or 'MCP_CLIENT' in os.environ
    logger.info(f"Running in Claude desktop environment: {in_claude_desktop}")
    
    # Load configuration and check environment
    config = load_config()
    redmine_url = config.get('redmine_url')
    logger.info(f"Configured Redmine URL: {redmine_url}")
    
    # Set mock mode if running in test mode
    if os.environ.get('REDMINE_TEST_MODE', '').lower() == 'true':
        os.environ['REDMINE_MOCK_MODE'] = 'true'
        logger.info("Running in test mode with mock Redmine responses")
    
    try:
        if os.environ.get('MCP_DIRECT_RESPONSE', '').lower() == 'true':
            # Directly respond to MCP client without starting web server
            logger.info("Direct MCP response mode enabled")
            simulate_mcp_response()
            time.sleep(0.5)  # Brief pause
            # Then start the server normally as fallback
        
        run_server()
    except Exception as e:
        logger.error(f"Error running server: {str(e)}")
        sys.exit(1)

"""
Main entry point for the Redmine MCP Server
"""

import logging
from app.mcp_server import app, run_server
from app.config import setup_logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("Starting Redmine MCP Server")
    run_server()

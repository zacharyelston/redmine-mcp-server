#!/usr/bin/env python3
"""
Standard Model Context Protocol (MCP) implementation for Redmine
This implementation follows the MCP spec for direct communication with AI assistants
"""

import json
import logging
import os
import sys
import time
import traceback
from threading import Thread

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("redmine_mcp.log"),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("redmine_mcp")

# Import Redmine API (with mock mode support)
try:
    from app.redmine_api import RedmineAPI
    from app.config import load_config
except ImportError:
    logger.error("Failed to import Redmine API modules. Make sure you're running from the correct directory.")
    sys.exit(1)

class RedmineMCPServer:
    """MCP server implementation for Redmine integration"""
    
    def __init__(self):
        """Initialize the MCP server"""
        self.config = load_config()
        self.redmine_url = self.config.get('redmine_url', 'http://0.0.0.0:3000')
        self.redmine_api_key = self.config.get('redmine_api_key')
        self.project_id = self.config.get('project_id', 1)
        
        # Check for mock mode
        self.mock_mode = os.environ.get('REDMINE_MOCK_MODE', '').lower() == 'true'
        if self.mock_mode:
            logger.info("Running in mock mode - Redmine API calls will return simulated data")
        
        # Initialize Redmine API client
        self.redmine = RedmineAPI(self.redmine_url, self.redmine_api_key)
        
        # Session state
        self.initialized = False
        self.request_counter = 0
        self.last_activity = time.time()
        
        logger.info(f"Redmine MCP Server initialized with URL: {self.redmine_url}")
        if self.mock_mode:
            logger.info("Mock mode active - will simulate Redmine responses")
    
    def start(self):
        """Start the MCP server main loop"""
        logger.info("Starting Redmine MCP Server")
        
        # Start background health check thread
        health_thread = Thread(target=self._background_health_check, daemon=True)
        health_thread.start()
        
        try:
            # Main processing loop
            for line in sys.stdin:
                try:
                    # Process each line from stdin as a JSON-RPC message
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Parse the JSON-RPC message
                    message = json.loads(line)
                    self._process_message(message)
                    
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode JSON message: {line}")
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    traceback.print_exc(file=sys.stderr)
        
        except KeyboardInterrupt:
            logger.info("Received interrupt, shutting down")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {str(e)}")
            traceback.print_exc(file=sys.stderr)
        
        logger.info("MCP Server shutting down")
    
    def _process_message(self, message):
        """Process an incoming JSON-RPC message"""
        method = message.get('method')
        params = message.get('params', {})
        message_id = message.get('id')
        
        logger.info(f"Received message: method={method}, id={message_id}")
        
        if method == 'initialize':
            self._handle_initialize(message_id, params)
        elif method == 'shutdown':
            self._handle_shutdown(message_id, params)
        elif method == 'execute':
            self._handle_execute(message_id, params)
        elif method == 'notifications/cancelled':
            # Cancellation notification
            logger.info(f"Request cancelled: {params}")
        else:
            logger.warning(f"Unknown method: {method}")
            self._send_error(message_id, -32601, f"Method '{method}' not found")
    
    def _handle_initialize(self, message_id, params):
        """Handle initialize request"""
        logger.info("Handling initialization request")
        
        try:
            protocol_version = params.get('protocolVersion')
            logger.info(f"Client requested protocol version: {protocol_version}")
            
            # Send capability response
            response = {
                "jsonrpc": "2.0",
                "id": message_id,
                "result": {
                    "capabilities": {
                        "execute": True,
                        "resourcesAccess": True,
                        "promptTemplates": True
                    },
                    "serverInfo": {
                        "name": "redmine-mcp-server",
                        "version": "0.1.0"
                    }
                }
            }
            
            self._send_response(response)
            self.initialized = True
            logger.info("Initialization complete")
            
            # Test Redmine connection in background
            Thread(target=self._test_redmine_connection, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            self._send_error(message_id, -32603, f"Initialization failed: {str(e)}")
    
    def _handle_shutdown(self, message_id, params):
        """Handle shutdown request"""
        logger.info("Shutdown requested")
        
        response = {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": None
        }
        
        self._send_response(response)
        # Allow time for the response to be sent
        time.sleep(0.1)
        sys.exit(0)
    
    def _handle_execute(self, message_id, params):
        """Handle execute request"""
        self.request_counter += 1
        command = params.get('command', '')
        arguments = params.get('arguments', {})
        
        logger.info(f"Execute request #{self.request_counter}: command={command}")
        
        try:
            # Route to appropriate command handler
            if command == 'search_issues':
                result = self._handle_search_issues(arguments)
            elif command == 'get_issue':
                result = self._handle_get_issue(arguments)
            elif command == 'create_issue':
                result = self._handle_create_issue(arguments)
            elif command == 'update_issue':
                result = self._handle_update_issue(arguments)
            elif command == 'get_projects':
                result = self._handle_get_projects(arguments)
            elif command == 'create_wiki':
                result = self._handle_create_wiki(arguments)
            elif command == 'get_project_status':
                result = self._handle_get_project_status(arguments)
            else:
                logger.warning(f"Unknown command: {command}")
                self._send_error(message_id, -32601, f"Command '{command}' not found")
                return
            
            # Send success response
            response = {
                "jsonrpc": "2.0",
                "id": message_id,
                "result": result
            }
            self._send_response(response)
            logger.info(f"Successfully executed command: {command}")
            
        except Exception as e:
            logger.error(f"Error executing command {command}: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            self._send_error(message_id, -32603, f"Error executing command: {str(e)}")
    
    def _handle_search_issues(self, arguments):
        """Handle search_issues command"""
        project_id = arguments.get('project_id', self.project_id)
        query = arguments.get('query', '')
        limit = arguments.get('limit', 10)
        
        logger.info(f"Searching issues: project_id={project_id}, query={query}")
        
        try:
            issues = self.redmine.get_issues(project_id=project_id, limit=limit)
            
            # If there's a query string, filter results
            if query:
                filtered_issues = []
                for issue in issues:
                    if (query.lower() in issue.get('subject', '').lower() or 
                        query.lower() in issue.get('description', '').lower()):
                        filtered_issues.append(issue)
                issues = filtered_issues
            
            return {
                "issues": issues,
                "count": len(issues),
                "project_id": project_id
            }
        
        except Exception as e:
            logger.error(f"Error searching issues: {str(e)}")
            if self.mock_mode:
                # Return mock data in case of failure
                return {
                    "issues": [
                        {"id": 1, "subject": "Mock Issue 1", "description": "This is a mock issue"},
                        {"id": 2, "subject": "Mock Issue 2", "description": "Another mock issue"}
                    ],
                    "count": 2,
                    "project_id": project_id,
                    "mock_data": True
                }
            raise
    
    def _handle_get_issue(self, arguments):
        """Handle get_issue command"""
        issue_id = arguments.get('issue_id')
        
        if not issue_id:
            raise ValueError("issue_id is required")
        
        logger.info(f"Getting issue: issue_id={issue_id}")
        
        try:
            issue = self.redmine.get_issue(issue_id)
            return {"issue": issue}
        
        except Exception as e:
            logger.error(f"Error getting issue: {str(e)}")
            if self.mock_mode:
                # Return mock data in case of failure
                return {
                    "issue": {
                        "id": issue_id,
                        "subject": f"Mock Issue {issue_id}",
                        "description": "This is a mock issue description",
                        "status": {"name": "In Progress"},
                        "created_on": "2025-04-01T10:00:00Z",
                        "updated_on": "2025-04-02T15:30:00Z"
                    },
                    "mock_data": True
                }
            raise
    
    def _handle_create_issue(self, arguments):
        """Handle create_issue command"""
        subject = arguments.get('subject')
        description = arguments.get('description')
        project_id = arguments.get('project_id', self.project_id)
        
        if not subject or not description:
            raise ValueError("subject and description are required")
        
        logger.info(f"Creating issue: project_id={project_id}, subject={subject}")
        
        try:
            response = self.redmine.create_issue(
                project_id=project_id,
                subject=subject,
                description=description,
                tracker_id=arguments.get('tracker_id'),
                category_id=arguments.get('category_id')
            )
            
            return {
                "success": True,
                "issue": response.get("issue", {})
            }
        
        except Exception as e:
            logger.error(f"Error creating issue: {str(e)}")
            if self.mock_mode:
                # Return mock data in case of failure
                return {
                    "success": True,
                    "issue": {
                        "id": 999,
                        "subject": subject,
                        "project_id": project_id
                    },
                    "mock_data": True
                }
            raise
    
    def _handle_update_issue(self, arguments):
        """Handle update_issue command"""
        issue_id = arguments.get('issue_id')
        
        if not issue_id:
            raise ValueError("issue_id is required")
        
        logger.info(f"Updating issue: issue_id={issue_id}")
        
        try:
            response = self.redmine.update_issue(
                issue_id=issue_id,
                subject=arguments.get('subject'),
                description=arguments.get('description'),
                status_id=arguments.get('status_id'),
                tracker_id=arguments.get('tracker_id'),
                category_id=arguments.get('category_id'),
                notes=arguments.get('notes')
            )
            
            return {
                "success": True,
                "message": f"Issue #{issue_id} updated successfully"
            }
        
        except Exception as e:
            logger.error(f"Error updating issue: {str(e)}")
            if self.mock_mode:
                # Return mock data in case of failure
                return {
                    "success": True,
                    "message": f"Issue #{issue_id} updated successfully (mock)",
                    "mock_data": True
                }
            raise
    
    def _handle_get_projects(self, arguments):
        """Handle get_projects command"""
        logger.info("Getting projects list")
        
        if self.mock_mode:
            # Return mock projects data
            return {
                "projects": [
                    {"id": 1, "name": "Redmine MCP", "identifier": "redmine-mcp"},
                    {"id": 2, "name": "Documentation", "identifier": "docs"}
                ],
                "count": 2,
                "mock_data": True
            }
        
        # In real mode, we'd need to implement a get_projects method in the RedmineAPI class
        # For now, just return the current project
        try:
            project = self.redmine.get_project(self.project_id)
            return {
                "projects": [project],
                "count": 1
            }
        except Exception as e:
            logger.error(f"Error getting projects: {str(e)}")
            raise
    
    def _handle_create_wiki(self, arguments):
        """Handle create_wiki command"""
        project_id = arguments.get('project_id', self.project_id)
        title = arguments.get('title')
        text = arguments.get('text')
        
        if not title or not text:
            raise ValueError("title and text are required")
        
        logger.info(f"Creating/updating wiki page: project_id={project_id}, title={title}")
        
        try:
            wiki_page = self.redmine.create_wiki_page(
                project_id=project_id,
                title=title,
                text=text,
                comments=arguments.get('comments')
            )
            
            return {
                "success": True,
                "wiki_page": wiki_page
            }
        
        except Exception as e:
            logger.error(f"Error creating/updating wiki page: {str(e)}")
            if self.mock_mode:
                # Return mock data in case of failure
                return {
                    "success": True,
                    "wiki_page": {
                        "title": title,
                        "text": text[:50] + "..." if len(text) > 50 else text,
                        "project_id": project_id
                    },
                    "mock_data": True
                }
            raise
    
    def _handle_get_project_status(self, arguments):
        """Handle get_project_status command"""
        project_id = arguments.get('project_id', self.project_id)
        
        logger.info(f"Getting project status: project_id={project_id}")
        
        if self.mock_mode:
            # Return mock project status data
            return {
                "project": {
                    "id": project_id,
                    "name": "Redmine MCP",
                    "identifier": "redmine-mcp"
                },
                "issues": {
                    "total": 12,
                    "open": 5,
                    "closed": 7,
                    "by_status": {
                        "New": 2,
                        "In Progress": 3,
                        "Resolved": 0,
                        "Closed": 7
                    }
                },
                "members": 3,
                "activity": "High",
                "mock_data": True
            }
        
        # In real mode, we'd compile project statistics
        # For now, return a simplified status
        try:
            project = self.redmine.get_project(project_id)
            issues = self.redmine.get_issues(project_id=project_id, limit=100)
            
            # Count issues by status
            status_counts = {}
            for issue in issues:
                status_name = issue.get('status', {}).get('name', 'Unknown')
                status_counts[status_name] = status_counts.get(status_name, 0) + 1
            
            # Count open vs closed
            closed_count = status_counts.get('Closed', 0) + status_counts.get('Rejected', 0)
            open_count = sum(status_counts.values()) - closed_count
            
            return {
                "project": project,
                "issues": {
                    "total": len(issues),
                    "open": open_count,
                    "closed": closed_count,
                    "by_status": status_counts
                }
            }
        
        except Exception as e:
            logger.error(f"Error getting project status: {str(e)}")
            raise
    
    def _send_response(self, response):
        """Send JSON-RPC response to stdout"""
        try:
            json_response = json.dumps(response)
            print(json_response, flush=True)
            self.last_activity = time.time()
        except Exception as e:
            logger.error(f"Error sending response: {str(e)}")
    
    def _send_error(self, message_id, code, message):
        """Send JSON-RPC error response"""
        error_response = {
            "jsonrpc": "2.0",
            "id": message_id,
            "error": {
                "code": code,
                "message": message
            }
        }
        self._send_response(error_response)
    
    def _background_health_check(self):
        """Background thread for health checks"""
        logger.info("Starting background health check thread")
        
        while True:
            try:
                # Only perform checks after initialization
                if self.initialized:
                    # Test Redmine connection
                    logger.debug("Running background health check")
                    
                    # Check for inactivity timeout (5 minutes)
                    elapsed = time.time() - self.last_activity
                    if elapsed > 300:  # 5 minutes
                        logger.info(f"Inactivity timeout after {elapsed:.1f} seconds")
                        break
                    
                    # Test Redmine connection periodically
                    try:
                        if not self.mock_mode:
                            self.redmine.get_project(self.project_id)
                            logger.debug("Redmine connection successful")
                    except Exception as e:
                        logger.warning(f"Redmine connection check failed: {str(e)}")
                
                # Wait before next check
                time.sleep(30)
            
            except Exception as e:
                logger.error(f"Error in health check thread: {str(e)}")
                time.sleep(60)  # Wait longer after an error
    
    def _test_redmine_connection(self):
        """Test connection to Redmine server"""
        try:
            logger.info(f"Testing connection to Redmine at {self.redmine_url}")
            
            if self.mock_mode:
                logger.info("Mock mode active - skipping actual connection test")
                return
            
            project = self.redmine.get_project(self.project_id)
            logger.info(f"Successfully connected to Redmine. Project: {project.get('name', 'unknown')}")
        
        except Exception as e:
            logger.error(f"Failed to connect to Redmine: {str(e)}")

if __name__ == "__main__":
    # Check for environment variables
    if os.environ.get('REDMINE_DEBUG', '').lower() == 'true':
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Start MCP server
    server = RedmineMCPServer()
    server.start()

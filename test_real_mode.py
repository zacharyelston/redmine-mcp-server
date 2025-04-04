#!/usr/bin/env python3
"""
MCP Client Simulator for testing the Redmine MCP server in real mode
This script simulates MCP client requests to test the Redmine MCP server with actual Redmine connection
"""

import json
import os
import subprocess
import sys
import time
import threading

def send_message(process, message):
    """Send a JSON-RPC message to the MCP server process"""
    print(f"\n>>> Sending: {json.dumps(message)}")
    process.stdin.write(json.dumps(message) + "\n")
    process.stdin.flush()

def read_response(process):
    """Read a response from the MCP server process"""
    response = process.stdout.readline().strip()
    if response:
        try:
            parsed = json.loads(response)
            print(f"\n<<< Received: {json.dumps(parsed, indent=2)}")
            return parsed
        except json.JSONDecodeError:
            print(f"\n<<< Received non-JSON: {response}")
            return None
    return None

def output_reader(process):
    """Thread function to continuously read and display process output"""
    while True:
        try:
            line = process.stdout.readline()
            if not line:
                break
            print(f"<<< {line.strip()}")
        except:
            break

def run_mcp_test():
    """Run a test of the MCP server"""
    # Set environment variables for testing
    env = os.environ.copy()
    env["REDMINE_MOCK_MODE"] = "false"  # Use real mode
    env["REDMINE_DEBUG"] = "true"
    env["PYTHONUNBUFFERED"] = "1"
    
    print("Starting MCP test in REAL mode (not mock mode)")
    print("Will attempt to connect to actual Redmine server")
    
    # Start the MCP server process
    process = subprocess.Popen(
        ["python3", "mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=env
    )
    
    # Start a thread to read and display stderr
    stderr_thread = threading.Thread(target=lambda: print(process.stderr.read()), daemon=True)
    stderr_thread.start()
    
    try:
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "mcp-test-client",
                    "version": "0.1.0"
                }
            }
        }
        
        send_message(process, init_request)
        init_response = read_response(process)
        
        if not init_response:
            print("Error: No initialization response received")
            return
        
        # Wait a moment
        time.sleep(1)
        
        # Test getting projects
        projects_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "execute",
            "params": {
                "command": "get_projects",
                "arguments": {}
            }
        }
        
        send_message(process, projects_request)
        projects_response = read_response(process)
        
        # Wait a moment
        time.sleep(1)
        
        # Test searching issues
        issues_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "execute",
            "params": {
                "command": "search_issues",
                "arguments": {
                    "query": "bug"
                }
            }
        }
        
        send_message(process, issues_request)
        issues_response = read_response(process)
        
        # Wait a moment
        time.sleep(1)
        
        # Test creating an issue
        create_issue_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "execute",
            "params": {
                "command": "create_issue",
                "arguments": {
                    "subject": "Test Issue from MCP (Real Mode)",
                    "description": "This is a test issue created via the MCP protocol using real mode."
                }
            }
        }
        
        send_message(process, create_issue_request)
        create_issue_response = read_response(process)
        
        # Wait a moment
        time.sleep(1)
        
        # Send shutdown request
        shutdown_request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "shutdown",
            "params": {}
        }
        
        send_message(process, shutdown_request)
        shutdown_response = read_response(process)
        
        print("\nTest complete!")
    
    except KeyboardInterrupt:
        print("\nTest interrupted!")
    except Exception as e:
        print(f"\nError: {str(e)}")
    finally:
        try:
            # Make sure the process is terminated
            process.terminate()
            process.wait(timeout=2)
        except:
            pass

if __name__ == "__main__":
    run_mcp_test()

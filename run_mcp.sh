#!/bin/bash
# Run the Redmine MCP server in standard MCP mode

# Set environment variables
export PYTHONUNBUFFERED=1  # Important for stdio communication

# Check for debug flag
if [ "$1" == "--debug" ]; then
  export REDMINE_DEBUG=true
  echo "Debug mode enabled"
fi

# Check for mock mode
if [ "$1" == "--mock" ] || [ "$2" == "--mock" ]; then
  export REDMINE_MOCK_MODE=true
  echo "Mock mode enabled"
fi

# Check for Claude desktop environment
if [ -n "$CLAUDE_DESKTOP" ] || [ -n "$MCP_CLIENT" ]; then
  echo "Detected Claude desktop environment"
  export REDMINE_MOCK_MODE=false
  export REDMINE_DEBUG=true
fi

# Create log directory if it doesn't exist
mkdir -p logs

# Set log file
LOG_FILE="logs/mcp_$(date +%Y%m%d_%H%M%S).log"
echo "Logging to $LOG_FILE"

# Check if virtual environment exists
if [ -d "venv" ]; then
  echo "Using virtual environment"
  source venv/bin/activate
  PYTHON="python"
else
  echo "Using system Python"
  PYTHON="python3"
fi

echo "Starting Redmine MCP server..."
echo "Current time: $(date)"
echo "Redmine URL: ${REDMINE_URL:-http://0.0.0.0:3000}"

# Run the MCP server
$PYTHON mcp_server.py 2>> "$LOG_FILE"

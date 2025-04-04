#!/bin/bash
# Script specifically designed to run the MCP server in Claude desktop environment

# Set environment variables for Claude desktop mode
export CLAUDE_DESKTOP=true
export MCP_DIRECT_RESPONSE=true
export REDMINE_TEST_MODE=true
export REDMINE_MOCK_MODE=false
export MCP_DEBUG=true

# Log startup
echo "Starting Redmine MCP server in Claude desktop mode..."
if [ "$REDMINE_MOCK_MODE" = "true" ]; then
  echo "Using mock mode to avoid connection issues"
else
  echo "Using real mode - will attempt to connect to Redmine"
fi
echo "Current time: $(date)"
echo "Redmine URL: ${REDMINE_URL:-0.0.0.0:3000}"

# Create log directory if it doesn't exist
mkdir -p logs

# Run with increased timeout
if [ -d "venv" ]; then
    # Use virtual environment if available
    source venv/bin/activate
    python main.py 2>&1 | tee logs/claude_desktop_$(date +%Y%m%d_%H%M%S).log
else
    # Otherwise run directly
    python3 main.py 2>&1 | tee logs/claude_desktop_$(date +%Y%m%d_%H%M%S).log
fi

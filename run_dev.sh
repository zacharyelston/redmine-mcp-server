#!/bin/bash
# Development script to run the MCP server locally

# Set up virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    FRESH_ENV=true
else
    # Ask if user wants to recreate the environment
    read -p "Recreate virtual environment for clean install? (y/n) " RECREATE
    if [ "$RECREATE" = "y" ]; then
        echo "Removing existing virtual environment..."
        rm -rf venv
        echo "Creating fresh virtual environment..."
        python3 -m venv venv
        FRESH_ENV=true
    fi
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
if [ "$FRESH_ENV" = "true" ]; then
    echo "Installing dependencies in fresh environment..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "Updating dependencies..."
    pip install -r requirements.txt
fi

# Run the server
echo "Starting Redmine MCP Server in development mode..."
python main.py

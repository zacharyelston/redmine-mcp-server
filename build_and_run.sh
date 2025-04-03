#!/bin/bash
# Script to build and run the Docker container

echo "Building the Docker image..."
docker build -t redmine-mcp-server .

echo "Running the Docker container..."
docker run -d --name redmine-mcp \
  -p 5050:5050 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/credentials.yaml:/app/credentials.yaml \
  -e CREDENTIALS_PATH=credentials.yaml \
  redmine-mcp-server

echo "Container started! You can access the MCP server at http://localhost:5050/mcp"
echo "View logs with: docker logs redmine-mcp"

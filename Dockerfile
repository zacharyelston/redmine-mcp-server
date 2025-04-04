FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create log directory
RUN mkdir -p /app/logs

# Create MCP standard mode script and make it executable
RUN chmod +x /app/run_mcp.sh

# Expose the port the server runs on
EXPOSE 5050

# Run gunicorn server with config from environment
CMD ["gunicorn", "--bind", "0.0.0.0:5050", "main:app", "--workers", "4", "--timeout", "120"]

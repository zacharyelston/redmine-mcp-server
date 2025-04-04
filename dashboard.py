#!/usr/bin/env python3
"""
Redmine MCP Server Dashboard
A simple flask application to monitor the status of the Redmine MCP server
"""

import json
import requests
import datetime
import os
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Redmine MCP Server Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="10">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 1rem;
        }
        .container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            grid-gap: 1rem;
        }
        .card {
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            padding: 1rem;
            background: white;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        .status {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 3px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        .healthy {
            background-color: #d4edda;
            color: #155724;
        }
        .unhealthy {
            background-color: #f8d7da;
            color: #721c24;
        }
        .warning {
            background-color: #fff3cd;
            color: #856404;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            text-align: left;
            padding: 0.5rem;
            border-bottom: 1px solid #eee;
        }
        .timestamp {
            color: #666;
            font-size: 0.8rem;
            text-align: right;
        }
    </style>
</head>
<body>
    <h1>Redmine MCP Server Dashboard</h1>
    <p class="timestamp">Last updated: {{ timestamp }}</p>
    <div class="container">
        <div class="card">
            <div class="header">
                <h2>Server Status</h2>
                <span class="status {{ server_status_class }}">{{ server_status }}</span>
            </div>
            <table>
                <tr>
                    <td>Uptime</td>
                    <td>{{ uptime }}</td>
                </tr>
                <tr>
                    <td>MCP Protocol Version</td>
                    <td>2024-11-05</td>
                </tr>
                <tr>
                    <td>Server Version</td>
                    <td>{{ server_version }}</td>
                </tr>
                <tr>
                    <td>Redmine URL</td>
                    <td>{{ redmine_url }}</td>
                </tr>
                <tr>
                    <td>Redmine Connection</td>
                    <td class="{{ redmine_status_class }}">{{ redmine_status }}</td>
                </tr>
            </table>
        </div>
        
        <div class="card">
            <div class="header">
                <h2>MCP Capabilities</h2>
            </div>
            <table>
                <tr>
                    <th>Type</th>
                    <th>Count</th>
                </tr>
                {% for capability_type, count in capabilities.items() %}
                <tr>
                    <td>{{ capability_type }}</td>
                    <td>{{ count }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        
        <div class="card">
            <div class="header">
                <h2>Resource Usage</h2>
            </div>
            <table>
                <tr>
                    <td>CPU</td>
                    <td>{{ cpu_usage }}%</td>
                </tr>
                <tr>
                    <td>Memory</td>
                    <td>{{ memory_usage }}</td>
                </tr>
                <tr>
                    <td>Disk</td>
                    <td>{{ disk_usage }}</td>
                </tr>
            </table>
        </div>
        
        <div class="card">
            <div class="header">
                <h2>Request Statistics</h2>
            </div>
            <table>
                <tr>
                    <td>Total Requests</td>
                    <td>{{ request_stats['total'] }}</td>
                </tr>
                <tr>
                    <td>Successful</td>
                    <td>{{ request_stats['successful'] }}</td>
                </tr>
                <tr>
                    <td>Failed</td>
                    <td>{{ request_stats['failed'] }}</td>
                </tr>
                <tr>
                    <td>Average Response Time</td>
                    <td>{{ request_stats['avg_time'] }} ms</td>
                </tr>
            </table>
        </div>
    </div>
    
    <div class="card" style="margin-top: 1rem;">
        <div class="header">
            <h2>Recent Activity</h2>
        </div>
        <table>
            <tr>
                <th>Time</th>
                <th>Action</th>
                <th>Status</th>
            </tr>
            {% for activity in recent_activities %}
            <tr>
                <td>{{ activity['time'] }}</td>
                <td>{{ activity['action'] }}</td>
                <td class="{{ activity['status_class'] }}">{{ activity['status'] }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Render the dashboard"""
    
    # Get server status
    try:
        server_response = requests.get('http://localhost:5050/mcp', timeout=2)
        server_status = "Healthy" if server_response.status_code == 200 else "Unhealthy"
        server_status_class = "healthy" if server_response.status_code == 200 else "unhealthy"
        server_data = server_response.json()
        server_version = server_data.get('version', 'Unknown')
    except Exception as e:
        server_status = "Unhealthy"
        server_status_class = "unhealthy"
        server_version = "Unknown"
        server_data = {"capabilities": []}
    
    # Get Redmine status
    try:
        health_response = requests.get('http://localhost:5050/mcp/health', timeout=2)
        health_data = health_response.json()
        redmine_status = health_data.get('status', 'Unknown')
        redmine_url = health_data.get('redmine_url', 'Unknown')
        redmine_status_class = "healthy" if redmine_status == "healthy" else "unhealthy"
    except Exception as e:
        redmine_status = "Unhealthy"
        redmine_status_class = "unhealthy"
        redmine_url = "Unknown"
    
    # Count capabilities by type
    capabilities = {}
    for capability in server_data.get('capabilities', []):
        cap_type = capability.get('type', 'unknown')
        capabilities[cap_type] = capabilities.get(cap_type, 0) + 1
    
    # Simulate resource usage (in a real implementation, you'd get actual metrics)
    cpu_usage = "15"
    memory_usage = "128 MB"
    disk_usage = "2.1 GB"
    
    # Simulate request statistics
    request_stats = {
        "total": 42,
        "successful": 38,
        "failed": 4,
        "avg_time": 120
    }
    
    # Simulate recent activities
    recent_activities = [
        {"time": "01:51:23", "action": "Initialize MCP", "status": "Success", "status_class": "healthy"},
        {"time": "01:51:24", "action": "Connect to Redmine", "status": "Failed", "status_class": "unhealthy"},
        {"time": "01:52:05", "action": "Get Projects", "status": "Success", "status_class": "healthy"},
        {"time": "01:53:12", "action": "Create Issue", "status": "Success", "status_class": "healthy"},
        {"time": "01:54:45", "action": "Update Wiki", "status": "Warning", "status_class": "warning"}
    ]
    
    # Calculate uptime (in a real implementation, you'd get actual uptime)
    uptime = "32 minutes"
    
    # Current timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return render_template_string(
        HTML_TEMPLATE,
        timestamp=timestamp,
        server_status=server_status,
        server_status_class=server_status_class,
        server_version=server_version,
        redmine_url=redmine_url,
        redmine_status=redmine_status,
        redmine_status_class=redmine_status_class,
        capabilities=capabilities,
        cpu_usage=cpu_usage,
        memory_usage=memory_usage,
        disk_usage=disk_usage,
        request_stats=request_stats,
        recent_activities=recent_activities,
        uptime=uptime
    )

@app.route('/api/status')
def api_status():
    """Return server status as JSON"""
    try:
        # Get server status
        server_response = requests.get('http://localhost:5050/mcp', timeout=2)
        server_data = server_response.json() if server_response.status_code == 200 else {}
        
        # Get Redmine status
        health_response = requests.get('http://localhost:5050/mcp/health', timeout=2)
        health_data = health_response.json() if health_response.status_code == 200 else {}
        
        return jsonify({
            "server": {
                "status": "healthy" if server_response.status_code == 200 else "unhealthy",
                "version": server_data.get("version", "Unknown"),
                "capabilities": server_data.get("capabilities", [])
            },
            "redmine": {
                "status": health_data.get("status", "unknown"),
                "url": health_data.get("redmine_url", "Unknown"),
                "message": health_data.get("message", "")
            },
            "timestamp": datetime.datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "server": {"status": "unhealthy", "error": str(e)},
            "redmine": {"status": "unknown"},
            "timestamp": datetime.datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('DASHBOARD_PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)

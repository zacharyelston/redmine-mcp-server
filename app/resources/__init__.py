"""
Resource handlers for Redmine MCP Server
"""

from flask import jsonify

def get_issues_resource(redmine, config):
    """
    Get issues as MCP resources
    
    Args:
        redmine: RedmineAPI instance
        config: Configuration dictionary
        
    Returns:
        JSON response with issues data
    """
    project_id = config.get('project_id', 1)
    
    # Get issues from Redmine
    issues = redmine.get_issues(project_id=project_id)
    
    # Transform to MCP resource format
    resource_data = {
        "resource_type": "issues",
        "items": []
    }
    
    for issue in issues:
        # Extract relevant issue data
        issue_data = {
            "id": issue.get('id'),
            "title": issue.get('subject'),
            "description": issue.get('description'),
            "status": issue.get('status', {}).get('name'),
            "priority": issue.get('priority', {}).get('name'),
            "category": issue.get('category', {}).get('name') if 'category' in issue else None,
            "tracker": issue.get('tracker', {}).get('name'),
            "created_on": issue.get('created_on'),
            "updated_on": issue.get('updated_on'),
            "author": issue.get('author', {}).get('name'),
            "assignee": issue.get('assigned_to', {}).get('name') if 'assigned_to' in issue else None,
            "done_ratio": issue.get('done_ratio')
        }
        
        resource_data['items'].append(issue_data)
    
    return jsonify(resource_data)

def get_projects_resource(redmine, config):
    """
    Get project data as MCP resource
    
    Args:
        redmine: RedmineAPI instance
        config: Configuration dictionary
        
    Returns:
        JSON response with project data
    """
    project_id = config.get('project_id', 1)
    
    # Get project from Redmine
    project = redmine.get_project(project_id)
    
    # Get categories and statuses
    categories = redmine.get_categories(project_id)
    statuses = redmine.get_statuses()
    
    # Transform to MCP resource format
    resource_data = {
        "resource_type": "project",
        "id": project.get('id'),
        "name": project.get('name'),
        "description": project.get('description'),
        "created_on": project.get('created_on'),
        "updated_on": project.get('updated_on'),
        "categories": [
            {
                "id": category.get('id'),
                "name": category.get('name')
            } for category in categories
        ],
        "statuses": [
            {
                "id": status.get('id'),
                "name": status.get('name'),
                "is_closed": status.get('is_closed')
            } for status in statuses
        ]
    }
    
    return jsonify(resource_data)

def get_wiki_resource(redmine, config):
    """
    Get wiki pages as MCP resources
    
    Args:
        redmine: RedmineAPI instance
        config: Configuration dictionary
        
    Returns:
        JSON response with wiki data
    """
    # This is a placeholder since we need to implement wiki page listing
    # In a real implementation, we would call redmine.get_wiki_pages()
    
    resource_data = {
        "resource_type": "wiki",
        "project_id": config.get('project_id', 1),
        "message": "Wiki resources are available through the create_wiki tool",
        "items": []
    }
    
    return jsonify(resource_data)

"""
Tool handlers for Redmine MCP Server
"""

import logging
from flask import jsonify

logger = logging.getLogger(__name__)

def create_issue_tool(redmine, data, config):
    """
    MCP tool to create a new issue in Redmine
    
    Args:
        redmine: RedmineAPI instance
        data: Request data
        config: Configuration dictionary
        
    Returns:
        JSON response with created issue data
    """
    # Get parameters from request
    subject = data.get('subject')
    description = data.get('description')
    
    # Validate required parameters
    if not subject or not description:
        return jsonify({
            "success": False,
            "message": "Missing required parameters: subject and description must be provided"
        }), 400
    
    # Get optional parameters with defaults from config
    project_id = data.get('project_id', config.get('project_id', 1))
    tracker_id = data.get('tracker_id', config.get('default_tracker_id', 2))
    category_id = data.get('category_id', config.get('default_category_id', 3))
    
    # Additional optional parameters
    priority_id = data.get('priority_id')
    assigned_to_id = data.get('assigned_to_id')
    parent_issue_id = data.get('parent_issue_id')
    fixed_version_id = data.get('fixed_version_id')
    
    try:
        # Create issue in Redmine
        result = redmine.create_issue(
            project_id=project_id,
            subject=subject,
            description=description,
            tracker_id=tracker_id,
            category_id=category_id,
            priority_id=priority_id,
            assigned_to_id=assigned_to_id,
            parent_issue_id=parent_issue_id,
            fixed_version_id=fixed_version_id
        )
        
        logger.info(f"Created issue #{result.get('issue', {}).get('id')}: {subject}")
        
        return jsonify({
            "success": True,
            "issue_id": result.get('issue', {}).get('id'),
            "message": f"Issue created successfully: {subject}"
        })
    
    except Exception as e:
        logger.error(f"Error creating issue: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to create issue: {str(e)}"
        }), 500

def update_issue_tool(redmine, data, config):
    """
    MCP tool to update an existing issue in Redmine
    
    Args:
        redmine: RedmineAPI instance
        data: Request data
        config: Configuration dictionary
        
    Returns:
        JSON response with update status
    """
    # Get issue ID from request
    issue_id = data.get('issue_id')
    
    # Validate required parameters
    if not issue_id:
        return jsonify({
            "success": False,
            "message": "Missing required parameter: issue_id must be provided"
        }), 400
    
    # Optional parameters to update
    subject = data.get('subject')
    description = data.get('description')
    tracker_id = data.get('tracker_id')
    category_id = data.get('category_id')
    priority_id = data.get('priority_id')
    assigned_to_id = data.get('assigned_to_id')
    status_id = data.get('status_id')
    notes = data.get('notes')
    
    # Ensure at least one field is being updated
    if not any([subject, description, tracker_id, category_id, priority_id, assigned_to_id, status_id, notes]):
        return jsonify({
            "success": False,
            "message": "No update parameters provided"
        }), 400
    
    try:
        # Update issue in Redmine
        result = redmine.update_issue(
            issue_id=issue_id,
            subject=subject,
            description=description,
            tracker_id=tracker_id,
            category_id=category_id,
            priority_id=priority_id,
            assigned_to_id=assigned_to_id,
            status_id=status_id,
            notes=notes
        )
        
        logger.info(f"Updated issue #{issue_id}")
        
        return jsonify({
            "success": True,
            "issue_id": issue_id,
            "message": f"Issue #{issue_id} updated successfully"
        })
    
    except Exception as e:
        logger.error(f"Error updating issue #{issue_id}: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to update issue #{issue_id}: {str(e)}"
        }), 500

def create_wiki_tool(redmine, data, config):
    """
    MCP tool to create or update a wiki page in Redmine
    
    Args:
        redmine: RedmineAPI instance
        data: Request data
        config: Configuration dictionary
        
    Returns:
        JSON response with created/updated wiki page data
    """
    # Get parameters from request
    title = data.get('title')
    text = data.get('text')
    
    # Validate required parameters
    if not title or not text:
        return jsonify({
            "success": False,
            "message": "Missing required parameters: title and text must be provided"
        }), 400
    
    # Get optional parameters
    project_id = data.get('project_id', config.get('project_id', 1))
    comments = data.get('comments')
    
    try:
        # Create/update wiki page in Redmine
        result = redmine.create_wiki_page(
            project_id=project_id,
            title=title,
            text=text,
            comments=comments
        )
        
        logger.info(f"Created/Updated wiki page '{title}' for project {project_id}")
        
        return jsonify({
            "success": True,
            "title": title,
            "message": f"Wiki page '{title}' created/updated successfully"
        })
    
    except Exception as e:
        logger.error(f"Error creating/updating wiki page '{title}': {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to create/update wiki page '{title}': {str(e)}"
        }), 500

def get_project_status_tool(redmine, data, config):
    """
    MCP tool to get current project status and summary
    
    Args:
        redmine: RedmineAPI instance
        data: Request data
        config: Configuration dictionary
        
    Returns:
        JSON response with project status data
    """
    # Get project ID from request or config
    project_id = data.get('project_id', config.get('project_id', 1))
    
    try:
        # Get project data
        project = redmine.get_project(project_id)
        
        # Get all issues for the project
        issues = redmine.get_issues(project_id=project_id)
        
        # Calculate statistics
        total_issues = len(issues)
        
        # Count issues by status
        status_counts = {}
        for issue in issues:
            status_name = issue.get('status', {}).get('name', 'Unknown')
            if status_name in status_counts:
                status_counts[status_name] += 1
            else:
                status_counts[status_name] = 1
        
        # Count issues by category
        category_counts = {}
        for issue in issues:
            if 'category' in issue:
                category_name = issue.get('category', {}).get('name', 'Unknown')
                if category_name in category_counts:
                    category_counts[category_name] += 1
                else:
                    category_counts[category_name] = 1
            else:
                # No category
                if 'Uncategorized' in category_counts:
                    category_counts['Uncategorized'] += 1
                else:
                    category_counts['Uncategorized'] = 1
        
        # Calculate progress percentage
        closed_issues = sum(count for status, count in status_counts.items() 
                           if 'closed' in status.lower() or status.lower() == 'resolved')
        progress_percentage = (closed_issues / total_issues * 100) if total_issues > 0 else 0
        
        # Prepare response
        status_data = {
            "success": True,
            "project": {
                "id": project.get('id'),
                "name": project.get('name'),
                "description": project.get('description')
            },
            "statistics": {
                "total_issues": total_issues,
                "closed_issues": closed_issues,
                "progress_percentage": round(progress_percentage, 2),
                "by_status": status_counts,
                "by_category": category_counts
            }
        }
        
        return jsonify(status_data)
    
    except Exception as e:
        logger.error(f"Error getting project status: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to get project status: {str(e)}"
        }), 500

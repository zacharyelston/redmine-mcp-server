"""
Redmine API Client for MCP Server
Provides a comprehensive wrapper around the Redmine REST API
"""

import logging
import os
import requests
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class RedmineAPI:
    """A wrapper for the Redmine REST API"""
    
    def __init__(self, url=None, api_key=None):
        """
        Initialize the Redmine API client
        
        Args:
            url (str): The base URL of the Redmine instance (e.g., 'http://localhost:3000')
            api_key (str): The API key for authentication
        """
        # Allow environment variable overrides
        self.base_url = url or os.environ.get('REDMINE_URL', 'http://localhost:3000')
        self.api_key = api_key or os.environ.get('REDMINE_API_KEY')
        
        # Ensure URL ends with a trailing slash
        if not self.base_url.endswith('/'):
            self.base_url = self.base_url + '/'
        
        if not self.api_key:
            logger.warning("No Redmine API key provided. Limited functionality will be available.")
        
        self.headers = {
            "Content-Type": "application/json"
        }
        
        # Only add API key header if one is provided
        if self.api_key:
            self.headers["X-Redmine-API-Key"] = self.api_key
            logger.debug(f"Redmine API client initialized with URL: {self.base_url}")
    
    def _make_request(self, method, endpoint, data=None, params=None, files=None):
        """
        Make a request to the Redmine API
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE)
            endpoint (str): API endpoint (e.g., 'issues.json')
            data (dict, optional): Data to send in the request body
            params (dict, optional): Query parameters
            files (dict, optional): Files to upload
            
        Returns:
            dict: The response data
        """
        url = urljoin(self.base_url, endpoint)
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, params=params)
            elif method == 'POST':
                if files:
                    # For file uploads, don't send JSON
                    headers_without_content_type = {k: v for k, v in self.headers.items() if k != 'Content-Type'}
                    response = requests.post(url, headers=headers_without_content_type, data=data, files=files)
                else:
                    response = requests.post(url, headers=self.headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if response.status_code >= 400:
                logger.error(f"Redmine API error: {response.status_code} - {response.text}")
                raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
            
            # For successful requests with no content
            if response.status_code == 204 or not response.text.strip():
                return {"success": True, "message": "Operation completed successfully"}
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to Redmine API: {str(e)}")
            raise Exception(f"Failed to communicate with Redmine API: {str(e)}")
    
    def get_issues(self, project_id=None, status_id=None, tracker_id=None, category_id=None, limit=25, offset=0):
        """
        Get a list of issues from Redmine with filtering options
        
        Args:
            project_id (str, optional): Filter by project ID
            status_id (str, optional): Filter by status ID
            tracker_id (str, optional): Filter by tracker ID
            category_id (str, optional): Filter by category ID
            limit (int, optional): Maximum number of issues to return
            offset (int, optional): Offset for pagination
            
        Returns:
            list: List of issue dictionaries
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if project_id:
            params["project_id"] = project_id
        
        if status_id:
            params["status_id"] = status_id
            
        if tracker_id:
            params["tracker_id"] = tracker_id
            
        if category_id:
            params["category_id"] = category_id
        
        try:
            response = self._make_request('GET', 'issues.json', params=params)
            return response.get('issues', [])
        
        except Exception as e:
            logger.error(f"Error getting issues: {str(e)}")
            raise
    
    def get_issue(self, issue_id, include=None):
        """
        Get a specific issue from Redmine
        
        Args:
            issue_id (int): The ID of the issue to retrieve
            include (list, optional): List of associations to include
            
        Returns:
            dict: The issue data
        """
        params = {}
        if include:
            if isinstance(include, list):
                include_str = ",".join(include)
                params.update({"include": include_str})
            else:
                include_str = str(include)
                params.update({"include": include_str})
        
        try:
            response = self._make_request('GET', f'issues/{issue_id}.json', params=params)
            return response.get('issue', {})
        
        except Exception as e:
            logger.error(f"Error getting issue #{issue_id}: {str(e)}")
            raise
    
    def create_issue(self, project_id, subject, description, tracker_id=None, category_id=None, 
                    priority_id=None, assigned_to_id=None, parent_issue_id=None, fixed_version_id=None):
        """
        Create a new issue in Redmine
        
        Args:
            project_id (str): The ID of the project where the issue will be created
            subject (str): The issue subject/title
            description (str): The issue description
            tracker_id (int, optional): The ID of the tracker (bug, feature, etc.)
            category_id (int, optional): The ID of the category
            priority_id (int, optional): The ID of the priority
            assigned_to_id (int, optional): The ID of the user to assign the issue to
            parent_issue_id (int, optional): The ID of the parent issue
            fixed_version_id (int, optional): The ID of the version
            
        Returns:
            dict: The created issue data
        """
        issue_data = {
            "issue": {
                "project_id": project_id,
                "subject": subject,
                "description": description
            }
        }
        
        # Add optional fields if provided
        optional_fields = {
            "tracker_id": tracker_id,
            "category_id": category_id,
            "priority_id": priority_id,
            "assigned_to_id": assigned_to_id,
            "parent_issue_id": parent_issue_id,
            "fixed_version_id": fixed_version_id
        }
        
        for field, value in optional_fields.items():
            if value is not None:
                issue_data["issue"][field] = value
        
        try:
            response = self._make_request('POST', 'issues.json', data=issue_data)
            logger.info(f"Created issue #{response.get('issue', {}).get('id')}")
            return response
        
        except Exception as e:
            logger.error(f"Error creating issue: {str(e)}")
            raise
    
    def update_issue(self, issue_id, subject=None, description=None, tracker_id=None, 
                    category_id=None, priority_id=None, assigned_to_id=None, 
                    status_id=None, notes=None):
        """
        Update an existing issue in Redmine
        
        Args:
            issue_id (int): The ID of the issue to update
            subject (str, optional): The updated subject/title
            description (str, optional): The updated description
            tracker_id (int, optional): The updated tracker ID
            category_id (int, optional): The updated category ID
            priority_id (int, optional): The updated priority ID
            assigned_to_id (int, optional): The updated assignee ID
            status_id (int, optional): The updated status ID
            notes (str, optional): Notes to add to the issue
            
        Returns:
            dict: Success message
        """
        issue_data = {"issue": {}}
        
        # Add fields that need to be updated
        optional_fields = {
            "subject": subject,
            "description": description,
            "tracker_id": tracker_id,
            "category_id": category_id,
            "priority_id": priority_id,
            "assigned_to_id": assigned_to_id,
            "status_id": status_id,
            "notes": notes
        }
        
        for field, value in optional_fields.items():
            if value is not None:
                issue_data["issue"][field] = value
        
        # Only proceed if there's something to update
        if not issue_data["issue"]:
            logger.warning(f"No updates provided for issue #{issue_id}")
            return {"success": True, "message": "No updates provided"}
        
        try:
            response = self._make_request('PUT', f'issues/{issue_id}.json', data=issue_data)
            logger.info(f"Updated issue #{issue_id}")
            return {"success": True, "message": f"Issue #{issue_id} updated successfully"}
        
        except Exception as e:
            logger.error(f"Error updating issue #{issue_id}: {str(e)}")
            raise
    
    def create_wiki_page(self, project_id, title, text, comments=None):
        """
        Create or update a wiki page in a project
        
        Args:
            project_id (str): The ID of the project
            title (str): The title of the wiki page
            text (str): The content of the wiki page
            comments (str, optional): Comments about the update
            
        Returns:
            dict: The created/updated wiki page data
        """
        wiki_page_data = {
            "wiki_page": {
                "text": text
            }
        }
        
        if comments:
            wiki_page_data["wiki_page"]["comments"] = comments
        
        try:
            endpoint = f'projects/{project_id}/wiki/{title}.json'
            response = self._make_request('PUT', endpoint, data=wiki_page_data)
            logger.info(f"Created/Updated wiki page '{title}' for project {project_id}")
            return response.get('wiki_page', {})
        
        except Exception as e:
            logger.error(f"Error creating/updating wiki page '{title}' for project {project_id}: {str(e)}")
            raise
    
    def get_project(self, project_id):
        """
        Get a specific project from Redmine
        
        Args:
            project_id (str): The ID or identifier of the project
            
        Returns:
            dict: The project data
        """
        try:
            response = self._make_request('GET', f'projects/{project_id}.json')
            return response.get('project', {})
        
        except Exception as e:
            logger.error(f"Error getting project {project_id}: {str(e)}")
            raise
    
    def get_categories(self, project_id):
        """
        Get issue categories for a project
        
        Args:
            project_id (str): The ID or identifier of the project
            
        Returns:
            list: List of category dictionaries
        """
        try:
            response = self._make_request('GET', f'projects/{project_id}/issue_categories.json')
            return response.get('issue_categories', [])
        
        except Exception as e:
            logger.error(f"Error getting categories for project {project_id}: {str(e)}")
            raise
    
    def get_statuses(self):
        """
        Get a list of issue statuses from Redmine
        
        Returns:
            list: List of status dictionaries
        """
        try:
            response = self._make_request('GET', 'issue_statuses.json')
            return response.get('issue_statuses', [])
        
        except Exception as e:
            logger.error(f"Error getting statuses: {str(e)}")
            raise

"""YouTrack API client for retrieving issues."""

import json
import logging
from typing import List, Dict, Any, Optional, Iterator
from urllib.parse import urljoin, urlencode

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from config import YouTrackConfig

logger = logging.getLogger(__name__)
console = Console()


class YouTrackAPIError(Exception):
    """Custom exception for YouTrack API errors."""
    pass


class YouTrackClient:
    """Client for interacting with YouTrack REST API."""
    
    def __init__(self, config: YouTrackConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {config.api_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
    def _build_url(self, endpoint: str) -> str:
        """Build full API URL from endpoint."""
        return urljoin(f"{self.config.base_url}/api/", endpoint.lstrip('/'))
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((requests.RequestException, YouTrackAPIError))
    )
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with retry logic."""
        url = self._build_url(endpoint)
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise YouTrackAPIError("Authentication failed. Check your API token.") from e
            elif response.status_code == 403:
                raise YouTrackAPIError("Access forbidden. Check your permissions.") from e
            elif response.status_code == 404:
                raise YouTrackAPIError("Resource not found.") from e
            else:
                raise YouTrackAPIError(f"HTTP {response.status_code}: {response.text}") from e
        except requests.RequestException as e:
            raise YouTrackAPIError(f"Request failed: {str(e)}") from e
    
    def test_connection(self) -> bool:
        """Test the connection to YouTrack API."""
        try:
            # Try the user profile endpoint first (works for most users)
            try:
                response = self._make_request('GET', '/users/me')
                user_info = response.json()
                console.print(f"✅ Connected to YouTrack as: {user_info.get('name', 'Unknown')}")
                return True
            except YouTrackAPIError:
                # Fallback: try to get issues (this should work with basic permissions)
                response = self._make_request('GET', '/issues?$top=1')
                console.print("✅ Connected to YouTrack successfully")
                return True
        except YouTrackAPIError as e:
            console.print(f"❌ Failed to connect to YouTrack: {e}")
            return False
    
    def get_project_info(self, project_key: str) -> Dict[str, Any]:
        """Get information about a project."""
        response = self._make_request('GET', f'/admin/projects/{project_key}')
        return response.json()
    
    def get_issues_count(self, query: Optional[str] = None) -> Optional[int]:
        """Get total count of issues matching the query.
        
        Returns None if the count cannot be determined (header missing).
        This allows pagination to continue regardless of count accuracy.
        """
        params = {'$top': 1}  # We only need the count
        if query:
            params['query'] = query
            
        response = self._make_request('GET', '/issues', params=params)
        
        # YouTrack returns the total count in the X-YouTrack-TotalCount header
        total_count = response.headers.get('X-YouTrack-TotalCount')
        if total_count:
            return int(total_count)
        
        # Return None if header is missing - pagination will still work via batch size check
        return None
    
    def get_issues(
        self, 
        query: Optional[str] = None,
        fields: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Get all issues matching the query, yielding them in batches.
        
        Args:
            query: YouTrack query string (e.g., "project: {PROJECT_KEY}")
            fields: Comma-separated list of fields to fetch
            progress_callback: Optional callback function for progress updates
        
        Yields:
            Dict: Individual issue data
        """
        if fields is None:
            fields = self.config.youtrack_fields if hasattr(self.config, 'youtrack_fields') else \
                "idReadable,summary,description,created,updated,resolved,reporter(name,email)," \
                "assignee(name,email),priority(name),state(name),tags(name),customFields(name,value)"
        
        # Build query for project filtering
        if self.config.project_key and not query:
            query = f"project: {{{self.config.project_key}}}"
        elif self.config.project_key and query:
            query = f"project: {{{self.config.project_key}}} and ({query})"
        
        # Get total count for progress tracking (may be None if header missing)
        total_count = self.get_issues_count(query)
        if total_count:
            console.print(f"📊 Found {total_count} issues to export")
        else:
            console.print(f"📊 Fetching issues (count unknown, will fetch all available)")
        
        skip = 0
        processed = 0
        
        # Continue fetching until we get fewer issues than batch_size (or until total_count if known)
        while total_count is None or processed < total_count:
            params = {
                'fields': fields,
                '$top': self.config.batch_size,
                '$skip': skip
            }
            
            if query:
                params['query'] = query
            
            try:
                response = self._make_request('GET', '/issues', params=params)
                issues = response.json()
                
                if not issues:
                    break
                
                for issue in issues:
                    yield issue
                    processed += 1
                    
                    if progress_callback:
                        progress_callback(processed, total_count)
                
                skip += len(issues)
                
                # Break if we got fewer issues than requested (end of results)
                if len(issues) < self.config.batch_size:
                    break
                    
            except YouTrackAPIError as e:
                logger.error(f"Error fetching issues (skip={skip}): {e}")
                raise
    
    def export_issues_to_file(
        self, 
        output_file: str, 
        query: Optional[str] = None,
        fields: Optional[str] = None
    ) -> int:
        """
        Export issues to a JSON file.
        
        Args:
            output_file: Path to output file
            query: YouTrack query string
            fields: Comma-separated list of fields to fetch
            
        Returns:
            int: Number of issues exported
        """
        issues = []
        exported_count = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            # First, get total count (may be None if header missing)
            total_count = self.get_issues_count(query)
            task = progress.add_task("Exporting issues...", total=total_count if total_count else None)
            
            def update_progress(current: int, total: Optional[int]):
                progress.update(task, completed=current)
            
            try:
                for issue in self.get_issues(query=query, fields=fields, progress_callback=update_progress):
                    issues.append(issue)
                    exported_count += 1
                
                # Write to file
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(issues, f, indent=2, ensure_ascii=False)
                
                console.print(f"✅ Exported {exported_count} issues to {output_file}")
                return exported_count
                
            except Exception as e:
                console.print(f"❌ Export failed: {e}")
                raise

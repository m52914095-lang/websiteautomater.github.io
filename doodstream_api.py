"""
DoodStream API Integration Module
Handles file uploads, downloads, and metadata retrieval
"""

import requests
import json
import time
from typing import List, Dict, Optional, Tuple
from config import DOODSTREAM_API_KEY, DOODSTREAM_API_URL, MAX_RETRIES, RETRY_DELAY


class DoodStreamAPI:
    """Interface for DoodStream API operations"""
    
    def __init__(self, api_key: str, api_url: str = DOODSTREAM_API_URL):
        """
        Initialize DoodStream API client
        
        Args:
            api_key: DoodStream API key
            api_url: DoodStream API base URL
        """
        self.api_key = api_key
        self.api_url = api_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DetectiveConanAutomation/1.0'
        })
    
    def _make_request(self, endpoint: str, method: str = "GET", 
                     params: Dict = None, data: Dict = None, 
                     retries: int = MAX_RETRIES) -> Optional[Dict]:
        """
        Make API request with retry logic
        
        Args:
            endpoint: API endpoint
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            data: Request body data
            retries: Number of retries on failure
            
        Returns:
            JSON response or None on failure
        """
        url = f"{self.api_url}/{endpoint}"
        
        if params is None:
            params = {}
        params['key'] = self.api_key
        
        for attempt in range(retries):
            try:
                if method == "GET":
                    response = self.session.get(url, params=params, timeout=30)
                elif method == "POST":
                    response = self.session.post(url, params=params, json=data, timeout=30)
                else:
                    return None
                
                response.raise_for_status()
                return response.json()
            
            except requests.exceptions.RequestException as e:
                print(f"API request failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    return None
    
    def get_account_info(self) -> Optional[Dict]:
        """Get account information"""
        return self._make_request("account/info")
    
    def list_files(self, folder_id: Optional[str] = None, 
                   limit: int = 100, offset: int = 0) -> Optional[Dict]:
        """
        List files in account or specific folder
        
        Args:
            folder_id: Optional folder ID to list files from
            limit: Number of files to return
            offset: Offset for pagination
            
        Returns:
            List of files or None on failure
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        if folder_id:
            params['folder_id'] = folder_id
        
        return self._make_request("file/list", params=params)
    
    def search_files(self, query: str, limit: int = 100) -> Optional[Dict]:
        """
        Search for files by name
        
        Args:
            query: Search query
            limit: Maximum results to return
            
        Returns:
            Search results or None on failure
        """
        params = {
            'search': query,
            'limit': limit
        }
        return self._make_request("file/search", params=params)
    
    def get_file_info(self, file_id: str) -> Optional[Dict]:
        """
        Get detailed information about a file
        
        Args:
            file_id: File ID
            
        Returns:
            File information or None on failure
        """
        params = {'file_id': file_id}
        return self._make_request("file/info", params=params)
    
    def rename_file(self, file_id: str, new_name: str) -> bool:
        """
        Rename a file
        
        Args:
            file_id: File ID
            new_name: New file name
            
        Returns:
            True if successful, False otherwise
        """
        data = {
            'file_id': file_id,
            'name': new_name
        }
        result = self._make_request("file/rename", method="POST", data=data)
        return result is not None and result.get('status') == 'ok'
    
    def move_file(self, file_id: str, folder_id: str) -> bool:
        """
        Move file to different folder
        
        Args:
            file_id: File ID
            folder_id: Target folder ID
            
        Returns:
            True if successful, False otherwise
        """
        data = {
            'file_id': file_id,
            'folder_id': folder_id
        }
        result = self._make_request("file/move", method="POST", data=data)
        return result is not None and result.get('status') == 'ok'
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file
        
        Args:
            file_id: File ID
            
        Returns:
            True if successful, False otherwise
        """
        data = {'file_id': file_id}
        result = self._make_request("file/delete", method="POST", data=data)
        return result is not None and result.get('status') == 'ok'
    
    def create_folder(self, folder_name: str, parent_folder_id: Optional[str] = None) -> Optional[str]:
        """
        Create a new folder
        
        Args:
            folder_name: Name for new folder
            parent_folder_id: Optional parent folder ID
            
        Returns:
            New folder ID or None on failure
        """
        data = {'name': folder_name}
        if parent_folder_id:
            data['parent_id'] = parent_folder_id
        
        result = self._make_request("folder/create", method="POST", data=data)
        return result.get('folder_id') if result else None
    
    def get_download_url(self, file_id: str) -> Optional[str]:
        """
        Get direct download URL for a file
        
        Args:
            file_id: File ID
            
        Returns:
            Download URL or None on failure
        """
        result = self._make_request("file/download", params={'file_id': file_id})
        return result.get('url') if result else None


class FileSearcher:
    """Advanced file search and selection interface"""
    
    def __init__(self, api: DoodStreamAPI):
        """
        Initialize file searcher
        
        Args:
            api: DoodStreamAPI instance
        """
        self.api = api
        self.search_results = []
        self.selected_files = []
    
    def search(self, query: str, limit: int = 1000) -> List[Dict]:
        """
        Search for files
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of search results
        """
        print(f"Searching for: {query}")
        result = self.api.search_files(query, limit=limit)
        
        if result and 'files' in result:
            self.search_results = result['files']
            print(f"Found {len(self.search_results)} results")
            return self.search_results
        
        print("No results found")
        return []
    
    def display_results(self, start: int = 0, count: int = 20) -> None:
        """
        Display search results in paginated format
        
        Args:
            start: Starting index
            count: Number of results to display
        """
        end = min(start + count, len(self.search_results))
        print(f"\n=== Search Results ({start + 1}-{end} of {len(self.search_results)}) ===")
        
        for i, file in enumerate(self.search_results[start:end], start=start):
            print(f"{i + 1}. {file.get('name', 'Unknown')}")
            print(f"   ID: {file.get('id', 'N/A')}")
            print(f"   Size: {file.get('size', 'N/A')} bytes")
            print(f"   Created: {file.get('created', 'N/A')}")
            print()
    
    def select_files(self, indices: List[int]) -> None:
        """
        Select specific files from search results
        
        Args:
            indices: List of result indices to select (1-based)
        """
        self.selected_files = []
        for idx in indices:
            if 1 <= idx <= len(self.search_results):
                self.selected_files.append(self.search_results[idx - 1])
        
        print(f"Selected {len(self.selected_files)} files for download")
    
    def get_selected_files(self) -> List[Dict]:
        """Get list of selected files"""
        return self.selected_files


# Test API connection
if __name__ == "__main__":
    api = DoodStreamAPI(DOODSTREAM_API_KEY)
    
    print("=== Testing DoodStream API ===")
    
    # Test account info
    print("\nFetching account info...")
    account = api.get_account_info()
    if account:
        print(f"Account: {json.dumps(account, indent=2)}")
    else:
        print("Failed to fetch account info")
    
    # Test file listing
    print("\nListing files...")
    files = api.list_files(limit=5)
    if files:
        print(f"Files: {json.dumps(files, indent=2)}")
    else:
        print("Failed to list files")
    
    # Test search
    print("\nSearching for files...")
    searcher = FileSearcher(api)
    results = searcher.search("Detective Conan", limit=10)
    if results:
        searcher.display_results(count=5)

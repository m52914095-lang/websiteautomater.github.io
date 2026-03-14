"""
Detective Conan Automation - Main Orchestrator
Coordinates batch processing, search, DoodStream sync, and website updates
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from config import (
    DOODSTREAM_API_KEY, XOR_ENCRYPTION_KEY, PASSWORD_HASH_KEY,
    LOG_FILE, LOG_LEVEL, FOLDER_MAPPING
)
from encryption import EncryptionManager
from doodstream_api import DoodStreamAPI, FileSearcher
from batch_processor import BatchProcessor, TitleCustomizer, RangeParser


# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutomationOrchestrator:
    """Main orchestrator for Detective Conan automation"""
    
    def __init__(self):
        """Initialize automation orchestrator"""
        self.api = DoodStreamAPI(DOODSTREAM_API_KEY)
        self.encryption = EncryptionManager(XOR_ENCRYPTION_KEY, PASSWORD_HASH_KEY)
        self.batch_processor = BatchProcessor()
        self.title_customizer = TitleCustomizer()
        self.searcher = FileSearcher(self.api)
        self.episode_data = {}
        
        logger.info("Automation orchestrator initialized")
    
    def search_episodes(self, query: str, limit: int = 1000) -> List[Dict]:
        """
        Search for episodes on DoodStream
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of search results
        """
        logger.info(f"Searching for: {query}")
        results = self.searcher.search(query, limit=limit)
        logger.info(f"Found {len(results)} results")
        return results
    
    def display_search_results(self, page: int = 1, per_page: int = 20) -> None:
        """Display search results in paginated format"""
        start = (page - 1) * per_page
        self.searcher.display_results(start=start, count=per_page)
    
    def select_files_for_download(self, indices: List[int]) -> None:
        """Select files from search results for download"""
        self.searcher.select_files(indices)
        logger.info(f"Selected {len(indices)} files for download")
    
    def process_episode_ranges(self, range_string: str, 
                              category: str = "original_hard_sub") -> Dict:
        """
        Process episode ranges
        
        Args:
            range_string: Range string (e.g., "100-150, 200-250")
            category: Episode category
            
        Returns:
            Processing summary
        """
        logger.info(f"Processing ranges: {range_string}")
        self.batch_processor.clear()
        self.batch_processor.add_ranges(range_string, category)
        return self.batch_processor.get_summary()
    
    def customize_titles(self, category: str, format_string: str) -> None:
        """Customize title format for category"""
        self.title_customizer.set_format(category, format_string)
        logger.info(f"Updated title format for {category}")
    
    def sync_with_doodstream(self) -> Dict:
        """
        Sync all DoodStream files with website
        
        Returns:
            Sync summary
        """
        logger.info("Starting DoodStream synchronization")
        
        sync_summary = {
            'timestamp': datetime.now().isoformat(),
            'categories': {},
            'total_files': 0,
            'errors': []
        }
        
        try:
            # Fetch all files
            files_response = self.api.list_files(limit=5000)
            
            if not files_response or 'files' not in files_response:
                logger.error("Failed to fetch files from DoodStream")
                sync_summary['errors'].append("Failed to fetch files")
                return sync_summary
            
            files = files_response['files']
            logger.info(f"Fetched {len(files)} files from DoodStream")
            
            # Categorize files
            for file in files:
                file_name = file.get('name', '')
                folder = file.get('folder', '')
                
                # Determine category from folder
                category = self._determine_category(folder, file_name)
                
                if category not in sync_summary['categories']:
                    sync_summary['categories'][category] = []
                
                sync_summary['categories'][category].append({
                    'id': file.get('id'),
                    'name': file_name,
                    'folder': folder,
                    'size': file.get('size'),
                    'created': file.get('created')
                })
                
                sync_summary['total_files'] += 1
            
            logger.info(f"Synchronized {sync_summary['total_files']} files")
        
        except Exception as e:
            logger.error(f"Sync error: {e}")
            sync_summary['errors'].append(str(e))
        
        return sync_summary
    
    def _determine_category(self, folder: str, filename: str) -> str:
        """Determine episode category from folder and filename"""
        # Check folder mapping first
        for folder_name, category in FOLDER_MAPPING.items():
            if folder_name.lower() in folder.lower():
                return category
        
        # Pattern matching on filename
        filename_lower = filename.lower()
        
        if 'dub' in filename_lower or 'case closed' in filename_lower:
            return 'dub'
        elif 'hard sub' in filename_lower or 'hs' in filename_lower:
            return 'original_hard_sub'
        elif 'remaster' in filename_lower:
            return 'remastered_hard_sub'
        elif 'soft sub' in filename_lower or 'ss' in filename_lower:
            return 'original_soft_sub'
        
        return 'unknown'
    
    def encrypt_link(self, link: str) -> str:
        """Encrypt a DoodStream link"""
        return self.encryption.encrypt_link(link)
    
    def decrypt_link(self, encrypted_link: str) -> str:
        """Decrypt a DoodStream link"""
        return self.encryption.decrypt_link(encrypted_link)
    
    def save_episode_data(self, filename: str) -> None:
        """Save episode data to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.episode_data, f, indent=2)
            logger.info(f"Episode data saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save episode data: {e}")
    
    def load_episode_data(self, filename: str) -> None:
        """Load episode data from JSON file"""
        try:
            with open(filename, 'r') as f:
                self.episode_data = json.load(f)
            logger.info(f"Episode data loaded from {filename}")
        except Exception as e:
            logger.error(f"Failed to load episode data: {e}")
    
    def get_status(self) -> Dict:
        """Get current automation status"""
        return {
            'timestamp': datetime.now().isoformat(),
            'batch_processor': self.batch_processor.get_summary(),
            'selected_files': len(self.searcher.get_selected_files()),
            'episode_data_entries': len(self.episode_data),
            'title_formats': self.title_customizer.get_all_formats()
        }


# CLI Interface
def main():
    """Main CLI interface"""
    orchestrator = AutomationOrchestrator()
    
    print("=== Detective Conan Automation System ===\n")
    
    while True:
        print("\nOptions:")
        print("1. Search for episodes")
        print("2. Process episode ranges")
        print("3. Customize titles")
        print("4. Sync with DoodStream")
        print("5. Encrypt/Decrypt links")
        print("6. View status")
        print("7. Exit")
        
        choice = input("\nSelect option (1-7): ").strip()
        
        if choice == '1':
            query = input("Enter search query: ").strip()
            results = orchestrator.search_episodes(query)
            if results:
                orchestrator.display_search_results()
                indices = input("Select files (comma-separated indices): ").strip()
                try:
                    selected = [int(x.strip()) for x in indices.split(',')]
                    orchestrator.select_files_for_download(selected)
                except ValueError:
                    print("Invalid input")
        
        elif choice == '2':
            range_str = input("Enter episode ranges (e.g., 100-150, 200-250): ").strip()
            category = input("Enter category (original_hard_sub/dub/etc.): ").strip()
            try:
                summary = orchestrator.process_episode_ranges(range_str, category)
                print(f"\nSummary: {json.dumps(summary, indent=2)}")
            except ValueError as e:
                print(f"Error: {e}")
        
        elif choice == '3':
            category = input("Enter category (soft_sub/hard_sub/movie/dub): ").strip()
            format_str = input("Enter title format: ").strip()
            orchestrator.customize_titles(category, format_str)
        
        elif choice == '4':
            sync_result = orchestrator.sync_with_doodstream()
            print(f"\nSync Summary: {json.dumps(sync_result, indent=2)}")
        
        elif choice == '5':
            link = input("Enter link to encrypt/decrypt: ").strip()
            action = input("Encrypt (e) or Decrypt (d)? ").strip().lower()
            if action == 'e':
                encrypted = orchestrator.encrypt_link(link)
                print(f"Encrypted: {encrypted}")
            elif action == 'd':
                decrypted = orchestrator.decrypt_link(link)
                print(f"Decrypted: {decrypted}")
        
        elif choice == '6':
            status = orchestrator.get_status()
            print(f"\nStatus: {json.dumps(status, indent=2)}")
        
        elif choice == '7':
            print("Exiting...")
            break
        
        else:
            print("Invalid option")


if __name__ == "__main__":
    main()

"""
Batch Processing Module for Detective Conan Automation
Handles episode range selection and bulk operations
"""

import re
from typing import List, Tuple, Dict, Optional
from config import TITLE_FORMATS, EPISODE_RANGES


class EpisodeRange:
    """Represents a range of episodes"""
    
    def __init__(self, start: int, end: int):
        """
        Initialize episode range
        
        Args:
            start: Starting episode number
            end: Ending episode number (inclusive)
        """
        if start > end:
            raise ValueError(f"Start episode ({start}) cannot be greater than end ({end})")
        
        self.start = start
        self.end = end
    
    def __str__(self) -> str:
        return f"{self.start}-{self.end}"
    
    def __repr__(self) -> str:
        return f"EpisodeRange({self.start}, {self.end})"
    
    def contains(self, episode: int) -> bool:
        """Check if episode is in range"""
        return self.start <= episode <= self.end
    
    def get_episodes(self) -> List[int]:
        """Get all episode numbers in range"""
        return list(range(self.start, self.end + 1))
    
    def count(self) -> int:
        """Get total episodes in range"""
        return self.end - self.start + 1


class RangeParser:
    """Parses episode range strings"""
    
    @staticmethod
    def parse(range_string: str) -> List[EpisodeRange]:
        """
        Parse episode range string
        
        Supports formats:
        - "100-150" - single range
        - "100-150, 200-250" - multiple ranges
        - "100" - single episode
        
        Args:
            range_string: Range string to parse
            
        Returns:
            List of EpisodeRange objects
            
        Raises:
            ValueError: If range string is invalid
        """
        ranges = []
        
        # Split by comma for multiple ranges
        parts = [p.strip() for p in range_string.split(',')]
        
        for part in parts:
            # Match pattern: "start-end" or just "number"
            match = re.match(r'^(\d+)(?:-(\d+))?$', part)
            
            if not match:
                raise ValueError(f"Invalid range format: {part}")
            
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else start
            
            ranges.append(EpisodeRange(start, end))
        
        return ranges
    
    @staticmethod
    def validate_ranges(ranges: List[EpisodeRange], 
                       category: str = "original_hard_sub") -> bool:
        """
        Validate episode ranges against category limits
        
        Args:
            ranges: List of ranges to validate
            category: Episode category (original_hard_sub, dub, etc.)
            
        Returns:
            True if all ranges are valid
            
        Raises:
            ValueError: If any range exceeds category limits
        """
        if category not in EPISODE_RANGES:
            raise ValueError(f"Unknown category: {category}")
        
        min_ep, max_ep = EPISODE_RANGES[category]
        
        for r in ranges:
            if r.start < min_ep or r.end > max_ep:
                raise ValueError(
                    f"Range {r} exceeds limits for {category} ({min_ep}-{max_ep})"
                )
        
        return True


class BatchProcessor:
    """Processes batch operations on episode ranges"""
    
    def __init__(self):
        """Initialize batch processor"""
        self.ranges = []
        self.total_episodes = 0
    
    def add_ranges(self, range_string: str, category: str = "original_hard_sub") -> None:
        """
        Add episode ranges for processing
        
        Args:
            range_string: Range string (e.g., "100-150, 200-250")
            category: Episode category
        """
        try:
            ranges = RangeParser.parse(range_string)
            RangeParser.validate_ranges(ranges, category)
            
            self.ranges.extend(ranges)
            self.total_episodes = sum(r.count() for r in self.ranges)
            
            print(f"Added {len(ranges)} range(s), total episodes: {self.total_episodes}")
        
        except ValueError as e:
            print(f"Error parsing ranges: {e}")
            raise
    
    def get_episodes(self) -> List[int]:
        """Get all episodes from all ranges"""
        episodes = []
        for r in self.ranges:
            episodes.extend(r.get_episodes())
        return sorted(list(set(episodes)))  # Remove duplicates and sort
    
    def generate_titles(self, version: str = "HS") -> Dict[int, str]:
        """
        Generate titles for episodes in ranges
        
        Args:
            version: Version type (HS=Hard Sub, SS=Soft Sub)
            
        Returns:
            Dictionary mapping episode number to title
        """
        titles = {}
        format_template = TITLE_FORMATS.get("hard_sub" if version == "HS" else "soft_sub")
        
        for episode in self.get_episodes():
            titles[episode] = format_template.format(
                episode=episode,
                version=version
            )
        
        return titles
    
    def get_summary(self) -> Dict:
        """Get summary of batch operation"""
        return {
            'ranges': [str(r) for r in self.ranges],
            'total_ranges': len(self.ranges),
            'total_episodes': self.total_episodes,
            'episodes': self.get_episodes()
        }
    
    def clear(self) -> None:
        """Clear all ranges"""
        self.ranges = []
        self.total_episodes = 0


class TitleCustomizer:
    """Customizes episode titles"""
    
    def __init__(self):
        """Initialize title customizer"""
        self.formats = TITLE_FORMATS.copy()
    
    def set_format(self, category: str, format_string: str) -> None:
        """
        Set custom title format for category
        
        Args:
            category: Category (soft_sub, hard_sub, movie, dub)
            format_string: Format string with variables like {episode}, {version}
        """
        self.formats[category] = format_string
        print(f"Updated {category} format: {format_string}")
    
    def get_format(self, category: str) -> str:
        """Get title format for category"""
        return self.formats.get(category, "")
    
    def generate_title(self, category: str, **kwargs) -> str:
        """
        Generate title using format and variables
        
        Args:
            category: Episode category
            **kwargs: Variables for format string (episode, version, number, title, etc.)
            
        Returns:
            Formatted title
        """
        format_str = self.get_format(category)
        try:
            return format_str.format(**kwargs)
        except KeyError as e:
            print(f"Missing variable in format: {e}")
            return format_str
    
    def get_all_formats(self) -> Dict[str, str]:
        """Get all title formats"""
        return self.formats.copy()


# Test batch processing
if __name__ == "__main__":
    print("=== Testing Batch Processing ===\n")
    
    # Test range parsing
    print("1. Testing range parsing:")
    try:
        ranges = RangeParser.parse("100-150, 200-250, 300")
        for r in ranges:
            print(f"   {r} ({r.count()} episodes)")
    except ValueError as e:
        print(f"   Error: {e}")
    
    # Test batch processor
    print("\n2. Testing batch processor:")
    processor = BatchProcessor()
    processor.add_ranges("1-10, 50-55")
    summary = processor.get_summary()
    print(f"   Ranges: {summary['ranges']}")
    print(f"   Total episodes: {summary['total_episodes']}")
    print(f"   Episodes: {summary['episodes']}")
    
    # Test title generation
    print("\n3. Testing title generation:")
    titles = processor.generate_titles(version="HS")
    for ep, title in list(titles.items())[:3]:
        print(f"   Episode {ep}: {title}")
    
    # Test title customization
    print("\n4. Testing title customization:")
    customizer = TitleCustomizer()
    customizer.set_format("hard_sub", "[HS] Detective Conan Ep. {episode} - {version}")
    title = customizer.generate_title("hard_sub", episode=100, version="1080p")
    print(f"   Generated: {title}")

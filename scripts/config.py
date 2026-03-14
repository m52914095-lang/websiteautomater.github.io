"""
Detective Conan Automation - Configuration Module
Manages API keys, encryption settings, and title customization
"""

# DoodStream API Configuration
DOODSTREAM_API_KEY = "554366xrjxeza9m7e4m02v"
DOODSTREAM_API_URL = "https://api.doodstream.com"

# Encryption Keys
XOR_ENCRYPTION_KEY = "DetectiveConan2024"
PASSWORD_HASH_KEY = "ConanEncryptKey2024"

# Title Format Configuration
TITLE_FORMATS = {
    "soft_sub": "Detective Conan {episode} {version}",
    "hard_sub": "Detective Conan {episode} {version}",
    "movie": "Detective Conan - Movie {number}",
    "dub": "Case Closed - {title} {episode}"
}

# Episode Range Configuration
EPISODE_RANGES = {
    "original_hard_sub": (1, 1193),
    "original_soft_sub": (1, 1193),
    "remastered_hard_sub": (1, 500),
    "dub": (1, 130)
}

# Folder Mapping for DoodStream
FOLDER_MAPPING = {
    "Case Closed": "dub",
    "Hard Sub": "original_hard_sub",
    "Beta Remastered": "remastered_hard_sub",
    "Soft Sub": "original_soft_sub"
}

# Timezone Configuration
TIMEZONE = "America/Chicago"  # Central Time
SCHEDULE_HOURS = [7, 8, 9]  # 7-9 AM CT
SCHEDULE_DAY = 5  # Saturday (0=Monday, 5=Saturday)

# Logging Configuration
LOG_FILE = "automation.log"
LOG_LEVEL = "INFO"

# Retry Configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Search Configuration
MAX_SEARCH_RESULTS = 1000
BATCH_SIZE = 50  # Files per batch operation

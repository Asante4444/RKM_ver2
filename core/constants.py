"""Configuration constants for the application."""
import os

# Base paths - UPDATED TO NEW STRUCTURE
ASSETS_BASE = r"D:\2025\Video Games\Street Fighter 6\RKM_ver2\assets"
CHAR_PORTRAIT_DIR = os.path.join(ASSETS_BASE, "portraits")
RANK_PORTRAIT_DIR = os.path.join(ASSETS_BASE, "rank images")
QUOTES_JSON = os.path.join(ASSETS_BASE, "quotes", "character_quotes.json")

# Database paths - UPDATED
ACTIVE_DB_FOLDER = r"D:\2025\Video Games\Street Fighter 6\RKM_ver2\udc"
BACKUP_DB_FOLDER = r"D:\2025\Video Games\Street Fighter 6\RKM_ver2\udc_backups"
REPLAY_FOLDER = r"D:\Videos\OBS_recordings"
PREFERENCES_FILE = os.path.join(ACTIVE_DB_FOLDER, "preferences.json")

# Icons (if you have them)
ICON_FOLDER = os.path.join(ASSETS_BASE, "icons")
DARK_MODE_ICON = os.path.join(ICON_FOLDER, "sun-dark.svg")
LIGHT_MODE_ICON = os.path.join(ICON_FOLDER, "sun-light.svg")

# Layout constants
PORTRAIT_SIZE_SMALL = 160
PORTRAIT_SIZE_MAIN = 220
PORTRAIT_SPACING = 12
TOP_BAND_PADDING = 8
ADD_REPLAY_INPUT_WIDTH = 350
BUTTON_HEIGHT = 28
MAX_ROW_HEIGHT = 200

# Timers (in milliseconds)
PORTRAIT_ROTATION_INTERVAL = 60000  # 60 seconds
QUOTE_ROTATION_INTERVAL = 60000     # 60 seconds
RECYCLE_BIN_CHECK_INTERVAL = 300000 # 5 minutes
RECYCLE_BIN_AUTO_DELETE_DAYS = 30
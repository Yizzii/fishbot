import time
import pyautogui
import os
import json
import sys
from dotenv import load_dotenv
import logging

# Determine base path for files (bundled or local)
def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)  # .exe directory
    # Use main.py's directory for non-bundled runs
    return os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))

BASE_PATH = get_base_path()

# Configure logging
def setup_logging():
    logging.basicConfig(
        filename=os.path.join(BASE_PATH, 'fish.log'),
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.debug("Logging initialized")

# Load environment variables
load_dotenv(os.path.join(BASE_PATH, '.env'))

# Default paths if not set in .env
EXEC_FILE = os.getenv('EXEC_FILE', os.path.join(BASE_PATH, 'exec.txt'))
CONSOLE_FILE = os.getenv('CONSOLE_FILE', os.path.join(BASE_PATH, 'console.log'))
if not EXEC_FILE or not CONSOLE_FILE:
    logging.warning("EXEC_FILE or CONSOLE_FILE not set in .env, using defaults")

PLAYER_STATS_FILE = os.path.join(BASE_PATH, 'player_stats.json')
GLOBAL_STATS_FILE = os.path.join(BASE_PATH, 'global_stats.json')
FISHBASE_FILE = os.path.join(BASE_PATH, 'fishbase.json')

def load_balances():
    """Load balances from player_stats.json, return a dict with lowercase keys."""
    stats = load_player_stats()
    balances = {player: data.get("balance", 0.0) for player, data in stats.items()}
    logging.debug(f"Loaded balances: {balances}")
    return balances

def save_balances(username, balance):
    """Save a single user's balance to player_stats.json."""
    username_lower = username.lower()
    stats = load_player_stats()
    if username_lower in stats:
        stats[username_lower]["balance"] = balance
    else:
        stats[username_lower] = {
            "balance": balance,
            "total_casts": 0,
            "total_fish_caught": 0,
            "rarities": {
                "Common": 0,
                "Uncommon": 0,
                "Rare": 0,
                "Very Rare": 0,
                "Epic": 0,
                "Legendary": 0
            },
            "equipped_rod": "Old Rod",
            "equipped_bait": "Worm",
            "original_username": username
        }
    save_player_stats(stats)
    logging.debug(f"Saved balance for {username_lower}: {balance}")

def get_balance(username):
    """Get a user's balance from player_stats.json, initialize to 0 if not found."""
    username_lower = username.lower()
    balances = load_balances()
    return balances.get(username_lower, 0.0)

def update_balance(username, amount):
    """Update a user's balance in player_stats.json and return the new balance."""
    username_lower = username.lower()
    current_balance = get_balance(username)
    new_balance = current_balance + amount
    save_balances(username_lower, new_balance)
    return new_balance

def load_player_stats():
    """Load player stats from player_stats.json, return a dict with lowercase keys."""
    if os.path.exists(PLAYER_STATS_FILE):
        try:
            with open(PLAYER_STATS_FILE, "r") as file:
                stats = json.load(file)
                default_player_stats = {
                    "balance": 0.0,
                    "total_casts": 0,
                    "total_fish_caught": 0,
                    "rarities": {
                        "Common": 0,
                        "Uncommon": 0,
                        "Rare": 0,
                        "Very Rare": 0,
                        "Epic": 0,
                        "Legendary": 0
                    },
                    "equipped_rod": "Old Rod",
                    "equipped_bait": "Worm",
                    "original_username": ""
                }
                new_stats = {}
                for player, data in stats.items():
                    player_lower = player.lower()
                    if "original_username" not in data:
                        data["original_username"] = player
                    if "equipped_bait" not in data:
                        data["equipped_bait"] = "Worm"
                    if "balance" not in data:
                        data["balance"] = 0.0
                    for key in default_player_stats:
                        if key not in data:
                            data[key] = default_player_stats[key]
                    for rarity in default_player_stats["rarities"]:
                        if rarity not in data["rarities"]:
                            data["rarities"][rarity] = 0
                    new_stats[player_lower] = data
                logging.debug(f"Loaded player stats: {new_stats}")
                return new_stats
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Error loading player stats: {e}")
            return {}
    logging.debug("Player stats file not found, using empty stats")
    return {}

def save_player_stats(stats):
    """Save player stats to player_stats.json, preserving lowercase keys."""
    try:
        with open(PLAYER_STATS_FILE, "w") as file:
            json.dump(stats, file, indent=2)
        logging.debug(f"Saved player stats: {stats}")
    except IOError as e:
        logging.error(f"Error saving player stats: {e}")

def get_display_username(username):
    """Get the display username from player_stats.json, or return original."""
    username_lower = username.lower()
    stats = load_player_stats()
    if username_lower in stats and stats[username_lower].get("original_username"):
        return stats[username_lower]["original_username"]
    return username

def write_command(command):
    logging.debug(f"Writing command to {EXEC_FILE}: {command}")
    with open(EXEC_FILE, 'w', encoding='utf-8') as f:
        f.write(command)

def press_key():
    time.sleep(0.2)
    pyautogui.press('f1')

def press_key_no_delay():
    pyautogui.press('f1')

def commands(username):
    """Display a list of available commands and their descriptions."""
    username_lower = username.lower()
    display_username = get_display_username(username)
    logging.debug(f"Commands requested by {username}")

    
    command_list = [
        "!fish",
        "!gamble",
        "!balance",
        "!stats",
        "!givemoney",
        "!shop",
        "!shop bait",
        "!shop buy <item_name>"
    ]

    write_command(f"say [COMMANDS] > {', '.join(command_list)}")
    press_key()
    logging.debug(f"Displayed commands for {username}")
import time
import re
import os
import sys
from dotenv import load_dotenv
from modules.fish import cast_line, show_player_stats, show_global_stats_command, shop
from modules.economy import gamble, give_money
from modules.utils import write_command, press_key, press_key_no_delay, get_balance, setup_logging, BASE_PATH, commands
import logging

# Setup logging
setup_logging()

load_dotenv(os.path.join(BASE_PATH, '.env'))

CONSOLE_FILE = os.getenv('CONSOLE_FILE', os.path.join(BASE_PATH, 'console.log'))
PRIVILEGED_USERNAME = os.getenv('PRIVILEGED_USERNAME')
if not PRIVILEGED_USERNAME:
    logging.error("PRIVILEGED_USERNAME not set in .env. No user will have privileged access.")
    PRIVILEGED_USERNAME = None
else:
    PRIVILEGED_USERNAME = PRIVILEGED_USERNAME.lower()

COOLDOWNS = {
    "!fish": 6.0,
    "!gamble": 6.0,
    "!balance": 6.0,
    "!stats": 6.0,
    "!globalstats": 6.0,
    "!shop": 6.0,
    "!givemoney": 6.0,
    "!commands": 6.0
}
LAST_COMMAND_TIMES = {}

def check_cooldown(username, command):
    """Check if the player is on cooldown. Return (is_allowed, wait_time)."""
    username_lower = username.lower()
    if PRIVILEGED_USERNAME and username_lower == PRIVILEGED_USERNAME:
        logging.debug(f"No cooldown for {command} for {username}")
        return True, 0.0

    cooldown_duration = COOLDOWNS.get(command, 0.0)
    if cooldown_duration == 0.0:
        logging.debug(f"No cooldown for {command} for {username}")
        return True, 0.0

    current_time = time.time()
    for user in list(LAST_COMMAND_TIMES.keys()):
        for cmd in list(LAST_COMMAND_TIMES[user].keys()):
            if current_time - LAST_COMMAND_TIMES[user][cmd] > 60:
                del LAST_COMMAND_TIMES[user][cmd]
        if not LAST_COMMAND_TIMES[user]:
            del LAST_COMMAND_TIMES[user]

    if username_lower not in LAST_COMMAND_TIMES:
        LAST_COMMAND_TIMES[username_lower] = {}
    last_time = LAST_COMMAND_TIMES[username_lower].get(command, 0.0)
    time_since_last = current_time - last_time

    logging.debug(f"Checking cooldown for {username} ({username_lower}) on {command}. Last time: {last_time}, Current time: {current_time}, Time since last: {time_since_last}, Cooldown: {cooldown_duration}")

    if time_since_last >= cooldown_duration:
        LAST_COMMAND_TIMES[username_lower][command] = current_time
        logging.debug(f"Cooldown passed for {username} ({username_lower}) on {command}. Updated timestamp to {current_time}")
        return True, 0.0
    else:
        wait_time = cooldown_duration - time_since_last
        logging.debug(f"Cooldown active for {username} ({username_lower}) on {command}. Wait {wait_time} seconds")
        return False, wait_time

def listen(logFile):
    logFile.seek(0, os.SEEK_END)
    last_size = logFile.tell()
    while True:
        current_size = os.stat(logFile.name).st_size
        if current_size < last_size:
            logFile.seek(0, os.SEEK_SET)
            last_size = current_size
        line = logFile.readline()
        if not line:
            time.sleep(0.1)
            continue
        logging.debug(f"Read line: {line.strip()}")
        parse(line)
        last_size = logFile.tell()

def parse(line):
    regex = re.search(r"\[(?:ALL|(?:C)?(?:T)?)\]\s+(.*)‎(?:﹫\w+)?\s*(?:\[DEAD\])?:(?:\s)?(\S+)?\s(.*)?", line, flags=re.UNICODE)
    if regex:
        username = regex.group(1)
        command = regex.group(2)
        args = regex.group(3)
    else:
        username = ""
        command = ""
        args = ""

    logging.debug(f"Parsed command: username={username}, command={command}, args={args}")

    if not command:
        logging.debug("Skipping empty command")
        return

    is_allowed, wait_time = check_cooldown(username, command)
    if not is_allowed:
        return

    match command:
        case "!fish":
            cast_line(username)
        case "!gamble":
            if args:
                gamble(username, args)
            else:
                write_command(f"say [GAMBLE] >> {username}: Please specify an amount, 'all', or percentage like 50%, e.g., !gamble 10, !gamble all, !gamble 50%")
                press_key()
        case "!balance":
            balance = get_balance(username)
            write_command(f"say [BALANCE] >> {username}: Your current balance is ${round(balance, 2):,.2f}")
            press_key()
        case "!stats":
            show_player_stats(username)
        case "!globalstats":
            show_global_stats_command(username)
        case "!shop":
            shop(username, args)
        case "!givemoney":
            give_money(username, args)
        case "!commands":
            commands(username)

if __name__ == '__main__':
    log_file = open(CONSOLE_FILE, "r", encoding="utf-8")
    try:
        while True:
            listen(log_file)
    except KeyboardInterrupt:
        logging.info("Script terminated by user")
        print("galls gone")
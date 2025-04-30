import json
import random
import time
import os
from datetime import datetime
from modules.utils import write_command, press_key, get_balance, update_balance, load_player_stats, save_player_stats, get_display_username, BASE_PATH, FISHBASE_FILE, GLOBAL_STATS_FILE
from enum import Enum
import logging

FISHING_RODS = {
    "Old Rod": {"price": 0.0, "catch_rate": 0.25, "rarity_modifier": 1.0},
    "Average Rod": {"price": 1000.0, "catch_rate": 0.45, "rarity_modifier": 1.1},
    "Good Rod": {"price": 5000.0, "catch_rate": 0.65, "rarity_modifier": 1.2},
    "Super Rod": {"price": 50000.0, "catch_rate": 0.75, "rarity_modifier": 1.5}
}

FISHING_BAITS = {
    "Worm": {"price": 0.0, "catch_rate_boost": 0.0, "rarity_modifier": 1.0},
    "Minnow": {"price": 500.0, "catch_rate_boost": 0.10, "rarity_modifier": 1.1},
    "Shrimp": {"price": 2000.0, "catch_rate_boost": 0.15, "rarity_modifier": 1.2},
    "Crab": {"price": 10000.0, "catch_rate_boost": 0.20, "rarity_modifier": 1.3}
}

class TimeOfDay(Enum):
    Morning = 0
    Afternoon = 1
    Evening = 2
    Night = 3

class SeaWeatherCondition(Enum):
    ClearSkies = 0
    PartlyCloudy = 1
    Overcast = 2
    Fog = 3
    Rain = 4
    Thunderstorms = 5
    Windy = 6
    Calm = 7

class FishData:
    def __init__(self):
        self.Categories = []

class FishCategory:
    def __init__(self):
        self.Rarity = ""
        self.FishList = []

class Fish:
    def __init__(self):
        self.Name = ""
        self.Price = 0.0
        self.Weight = None

class FishWeight:
    def __init__(self):
        self.Min = 0.0
        self.Max = 0.0

def load_global_stats():
    default_stats = {
        "total_casts": 0,
        "total_fish_caught": 0,
        "rarities": {
            "Common": 0,
            "Uncommon": 0,
            "Rare": 0,
            "Very Rare": 0,
            "Epic": 0,
            "Legendary": 0
        }
    }
    if os.path.exists(GLOBAL_STATS_FILE):
        try:
            with open(GLOBAL_STATS_FILE, "r") as file:
                stats = json.load(file)
                for key in default_stats:
                    if key not in stats:
                        stats[key] = default_stats[key]
                for rarity in default_stats["rarities"]:
                    if rarity not in stats["rarities"]:
                        stats["rarities"][rarity] = 0
                logging.debug(f"Loaded global stats: {stats}")
                return stats
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Error loading global stats: {e}")
            return default_stats
    logging.debug("Global stats file not found, using default stats")
    return default_stats

def save_global_stats(stats):
    try:
        with open(GLOBAL_STATS_FILE, "w") as file:
            json.dump(stats, file, indent=2)
        logging.debug(f"Saved global stats: {stats}")
    except IOError as e:
        logging.error(f"Error saving global stats: {e}")

def cast_line(username):
    username_lower = username.lower()
    display_username = get_display_username(username)
    global_stats = load_global_stats()
    global_stats["total_casts"] += 1
    player_stats = load_player_stats()
    if username_lower not in player_stats:
        player_stats[username_lower] = {
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
            "original_username": username
        }
    player_stats[username_lower]["total_casts"] += 1
    equipped_rod = player_stats[username_lower]["equipped_rod"]
    equipped_bait = player_stats[username_lower]["equipped_bait"]
    rod_stats = FISHING_RODS.get(equipped_rod, FISHING_RODS["Old Rod"])
    bait_stats = FISHING_BAITS.get(equipped_bait, FISHING_BAITS["Worm"])
    catch_rate = min(1.0, rod_stats["catch_rate"] + bait_stats["catch_rate_boost"])
    combined_rarity_modifier = rod_stats["rarity_modifier"] * bait_stats["rarity_modifier"]
    weather = get_weather()
    write_command(f"say [GOFISH] ♌︎ {display_username} is casting their line with {weather[1]} using {equipped_rod} and {equipped_bait}...")
    press_key()
    time.sleep(1)
    if random.random() > catch_rate:
        write_command(f"say [GOFISH] > {display_username}: (ó﹏ò｡) You didn't catch anything, try again later...")
        press_key()
    else:
        fish_name, price, weight = get_fish_result(weather[0], combined_rarity_modifier)
        global_stats["total_fish_caught"] += 1
        player_stats[username_lower]["total_fish_caught"] += 1
        fish_data = load_fish_db()
        chosen_rarity = None
        for category in fish_data["Categories"]:
            if any(fish["Name"] == fish_name for fish in category["FishList"]):
                chosen_rarity = category["Rarity"]
                break
        if chosen_rarity:
            global_stats["rarities"][chosen_rarity] += 1
            player_stats[username_lower]["rarities"][chosen_rarity] += 1
        update_balance(username, price)
        write_command(f"say [GOFISH] > {display_username}: <>< You caught a ({chosen_rarity}) {fish_name}! It weighs {round(weight, 2)}lbs and is worth around ${round(price, 2):,.2f}. New balance: ${round(get_balance(username), 2):,.2f}")
        press_key()
    save_global_stats(global_stats)
    save_player_stats(player_stats)

def shop(username, args=None):
    username_lower = username.lower()
    display_username = get_display_username(username)
    args_lower = args.lower() if args else ""
    if args_lower == "bait":
        bait_list = [
            f"{bait}: ${bait_stats['price']:,.2f} (Catch Rate Boost: +{bait_stats['catch_rate_boost']*100:.2f}%, Rarity Boost: {bait_stats['rarity_modifier']:.2f}x)"
            for bait, bait_stats in FISHING_BAITS.items() if bait != "Worm"
        ]
        write_command(
            f"say [SHOP] > Baits - {', '.join(bait_list)}. Use !shop buy <bait_name>. See rods with !shop"
        )
        press_key()
        return
    if not args:
        rod_list = [
            f"{rod}: ${rod_stats['price']:,.2f} (Catch Rate: {rod_stats['catch_rate']*100:.2f}%, Rarity Boost: {rod_stats['rarity_modifier']:.2f}x)"
            for rod, rod_stats in FISHING_RODS.items() if rod != "Old Rod"
        ]
        write_command(
            f"say [SHOP] > Rods - {', '.join(rod_list)}. Use !shop buy <rod_name>."
        )
        press_key()
        return
    if args_lower.startswith("buy "):
        item_name = " ".join(args.split()[1:]).title()
        player_stats = load_player_stats()
        current_balance = get_balance(username)
        if item_name in FISHING_RODS:
            rod_stats = FISHING_RODS[item_name]
            price = rod_stats["price"]
            if price == 0.0:
                write_command(f"say [SHOP] > {display_username}: The Old Rod is free and already equipped by default!")
                press_key()
                return
            if current_balance < price:
                write_command(f"say [SHOP] > {display_username}: Not enough funds! Need ${price:,.2f}, you have ${current_balance:,.2f}")
                press_key()
                return
            update_balance(username, -price)
            player_stats[username_lower]["equipped_rod"] = item_name
            save_player_stats(player_stats)
            write_command(f"say [SHOP] > {display_username}: You bought {item_name} for ${price:,.2f}! It’s now equipped. New balance: ${round(get_balance(username), 2):,.2f}")
            press_key()
            return
        if item_name in FISHING_BAITS:
            bait_stats = FISHING_BAITS[item_name]
            price = bait_stats["price"]
            if price == 0.0:
                write_command(f"say [SHOP] > {display_username}: Worm bait is free and already equipped by default!")
                press_key()
                return
            if current_balance < price:
                write_command(f"say [SHOP] > {display_username}: Not enough funds! Need ${price:,.2f}, you have ${current_balance:,.2f}")
                press_key()
            update_balance(username, -price)
            player_stats[username_lower]["equipped_bait"] = item_name
            save_player_stats(player_stats)
            write_command(f"say [SHOP] > {display_username}: You bought {item_name} bait for ${price:,.2f}! It’s now equipped. New balance: ${round(get_balance(username), 2):,.2f}")
            press_key()
            return
        write_command(f"say [SHOP] > {display_username}: Invalid item name. See baits with !shop bait, See rods with !shop")
        press_key()
        return
    write_command(f"say [SHOP] > {display_username}: Invalid command. Use !shop, !shop bait, or !shop buy <item_name>")
    press_key()

def show_global_stats_command(username):
    from main import PRIVILEGED_USERNAME
    username_lower = username.lower()
    display_username = get_display_username(username)
    logging.debug(f"Global stats requested by {username}")
    if not PRIVILEGED_USERNAME or username_lower != PRIVILEGED_USERNAME:
        privileged_name = PRIVILEGED_USERNAME if PRIVILEGED_USERNAME else "the configured user"
        write_command(f"say [GLOBALSTATS] > {display_username}: Only {privileged_name} can use !globalstats.")
        press_key()
        logging.debug(f"Global stats access denied for {username}")
        return
    try:
        stats = load_global_stats()
        player_stats = load_player_stats()
        total_anglers = len(player_stats)
        rarities = stats["rarities"]
        write_command(
            f"say [GLOBALSTATS] Global Fishing Stats: Total Anglers: {total_anglers}, "
            f"Total Casts: {stats['total_casts']}, "
            f"Total Fish Caught: {stats['total_fish_caught']}, "
            f"Rarities - Common: {rarities['Common']}, Uncommon: {rarities['Uncommon']}, "
            f"Rare: {rarities['Rare']}, Very Rare: {rarities['Very Rare']}, "
            f"Epic: {rarities['Epic']}, Legendary: {rarities['Legendary']}"
        )
        press_key()
        logging.debug(f"Displayed global stats for {username}: {stats}, Total Anglers: {total_anglers}")
    except Exception as e:
        write_command(f"say [GLOBALSTATS] > {display_username}: Error retrieving global stats. Please try again later.")
        press_key()
        logging.error(f"Error in show_global_stats_command for {username}: {e}")

def show_player_stats(username):
    username_lower = username.lower()
    display_username = get_display_username(username)
    logging.debug(f"Player stats requested by {username}")
    try:
        stats = load_player_stats()
        if username_lower not in stats:
            write_command(f"say [STATS] > {display_username}: No stats available. Try fishing first!")
            press_key()
            logging.debug(f"No stats for {username}")
            return
        player_data = stats[username_lower]
        rarities = player_data["rarities"]
        equipped_rod = player_data["equipped_rod"]
        equipped_bait = player_data["equipped_bait"]
        write_command(
            f"say [STATS] {display_username}'s Stats: Equipped Rod: {equipped_rod}, Equipped Bait: {equipped_bait}, "
            f"Balance: ${round(player_data['balance'], 2):,.2f}, "
            f"Total Casts: {player_data['total_casts']}, "
            f"Total Fish Caught: {player_data['total_fish_caught']}, "
            f"Rarities - Common: {rarities['Common']}, Uncommon: {rarities['Uncommon']}, "
            f"Rare: {rarities['Rare']}, Very Rare: {rarities['Very Rare']}, "
            f"Epic: {rarities['Epic']}, Legendary: {rarities['Legendary']}"
        )
        press_key()
        logging.debug(f"Displayed player stats for {username}: {player_data}")
    except Exception as e:
        write_command(f"say [STATS] > {display_username}: Error retrieving stats. Please try again later.")
        press_key()
        logging.error(f"Error in show_player_stats for {username}: {e}")

def load_fish_db():
    try:
        with open(FISHBASE_FILE, "r") as file:
            json_data = file.read()
            fish_data = json.loads(json_data)
        return fish_data
    except (IOError, json.JSONDecodeError) as e:
        logging.error(f"Error loading fishbase.json: {e}")
        raise ValueError("Failed to load fish database")

def get_fish_result(sea_weather, combined_rarity_modifier):
    fish_data = load_fish_db()
    if fish_data:
        weather_modifier = get_rarity_modifier(sea_weather)
        total_modifier = weather_modifier * combined_rarity_modifier
        rarity_roll = random.random()
        chosen_rarity = choose_rarity(rarity_roll, fish_data["Categories"], total_modifier)
        chosen_category = next((category for category in fish_data["Categories"] if category["Rarity"] == chosen_rarity), None)
        if chosen_category:
            fish_list = chosen_category["FishList"]
            chosen_fish = random.choice(fish_list)
            random_weight = random.uniform(chosen_fish["Weight"]["Min"], chosen_fish["Weight"]["Max"])
            usd_price = chosen_fish["Price"] * random_weight
            return chosen_fish["Name"], usd_price, random_weight
    else:
        raise ValueError("fishData was null")

def get_weather():
    forecasted_weather = forecast_sea_weather()
    weather_description = get_weather_description(forecasted_weather)
    return forecasted_weather, weather_description

def forecast_sea_weather():
    current_time_of_day = get_current_time_of_day()
    base_condition = {
        TimeOfDay.Morning: SeaWeatherCondition.ClearSkies,
        TimeOfDay.Afternoon: SeaWeatherCondition.PartlyCloudy,
        TimeOfDay.Evening: SeaWeatherCondition.Overcast,
        TimeOfDay.Night: SeaWeatherCondition.ClearSkies,
    }.get(current_time_of_day, SeaWeatherCondition.ClearSkies)
    if random.random() <= 0.25:
        base_condition = random.choice(list(SeaWeatherCondition))
    return base_condition

def get_current_time_of_day():
    current_hour = datetime.now().hour
    if 6 <= current_hour < 12:
        return TimeOfDay.Morning
    elif 12 <= current_hour < 18:
        return TimeOfDay.Afternoon
    elif 18 <= current_hour < 24:
        return TimeOfDay.Evening
    else:
        return TimeOfDay.Night

def get_weather_description(condition):
    return {
        SeaWeatherCondition.ClearSkies: "Clear skies and calm seas",
        SeaWeatherCondition.PartlyCloudy: "Partly cloudy skies and gentle breeze",
        SeaWeatherCondition.Overcast: "Overcast skies and potential for rain",
        SeaWeatherCondition.Fog: "Foggy conditions and reduced visibility",
        SeaWeatherCondition.Rain: "Rainfall and choppy seas",
        SeaWeatherCondition.Thunderstorms: "Thunderstorms and rough seas and lightning",
        SeaWeatherCondition.Windy: "Windy conditions and high waves",
        SeaWeatherCondition.Calm: "Calm seas and little to no wind",
    }.get(condition, "Unknown weather condition")

def get_rarity_modifier(sea_weather):
    return {
        SeaWeatherCondition.ClearSkies: 1.0,
        SeaWeatherCondition.PartlyCloudy: 1.1,
        SeaWeatherCondition.Overcast: 1.2,
        SeaWeatherCondition.Fog: 0.8,
        SeaWeatherCondition.Rain: 0.7,
        SeaWeatherCondition.Thunderstorms: 0.5,
        SeaWeatherCondition.Windy: 0.9,
        SeaWeatherCondition.Calm: 1.1,
    }.get(sea_weather, 1.0)

def choose_rarity(roll, categories, modifier):
    probabilities = [rarity_chance(category["Rarity"]) * modifier for category in categories]
    total = sum(probabilities)
    if total == 0:
        return categories[-1]["Rarity"]
    probabilities = [p / total for p in probabilities]
    cumulative_chance = 0.0
    for i, prob in enumerate(probabilities):
        cumulative_chance += prob
        if roll <= cumulative_chance:
            return categories[i]["Rarity"]
    return categories[-1]["Rarity"]

def rarity_chance(rarity):
    return {
        "Common": 0.40,
        "Uncommon": 0.30,
        "Rare": 0.15,
        "Very Rare": 0.08,
        "Epic": 0.05,
        "Legendary": 0.02,
    }.get(rarity, 0.0)
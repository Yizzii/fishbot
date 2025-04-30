import json
import random
import os
from dotenv import load_dotenv
import logging
from modules.utils import write_command, press_key, get_balance, update_balance, load_player_stats, get_display_username, BASE_PATH, load_balances

load_dotenv(os.path.join(BASE_PATH, '.env'))

def gamble(username, amount_str):
    username_lower = username.lower()
    display_username = get_display_username(username)
    try:
        current_balance = get_balance(username)
        if current_balance <= 0:
            write_command(f"say [GAMBLE] > {display_username}: You have no funds to gamble! Current balance: ${round(current_balance, 2):,.2f}")
            press_key()
            return
        if amount_str.endswith("%"):
            try:
                percentage = float(amount_str[:-1])
                if not 1 <= percentage <= 100:
                    write_command(f"say [GAMBLE] > {display_username}: Percentage must be between 1% and 100%.")
                    press_key()
                    return
                amount = (percentage / 100) * current_balance
            except ValueError:
                write_command(f"say [GAMBLE] > {display_username}: Invalid percentage. Use a number between 1% and 100%, e.g., !gamble 50%")
                press_key()
                return
        elif amount_str.lower() == "all":
            amount = current_balance
        else:
            amount = float(amount_str)
        if amount <= 0:
            write_command(f"say [GAMBLE] > {display_username}: Please enter a positive amount.")
            press_key()
            return
        if amount > current_balance:
            write_command(f"say [GAMBLE] > {display_username}: You don't have enough funds! Current balance: ${round(current_balance, 2):,.2f}")
            press_key()
            return
        if random.random() < 0.5:
            winnings = amount
            update_balance(username, winnings)
            write_command(f"say [GAMBLE] > {display_username}: ( ')< You won ${round(winnings, 2):,.2f}! New balance: ${round(get_balance(username), 2):,.2f}")
        else:
            update_balance(username, -amount)
            write_command(f"say [GAMBLE] > {display_username}: ( ')> You lost ${round(amount, 2):,.2f}. New balance: ${round(get_balance(username), 2):,.2f}")
        press_key()
    except ValueError:
        write_command(f"say [GAMBLE] > {display_username}: Invalid amount. Use a number, 'all', or percentage like 50%, e.g., !gamble 10, !gamble all, !gamble 50%")
        press_key()

def give_money(username, args):
    username_lower = username.lower()
    display_username = get_display_username(username)
    if not args:
        write_command(f"say [GIVEMONEY] > {display_username}: Please specify a player and amount, e.g., !givemoney Bob 100")
        press_key()
        return
    try:
        args_list = args.split()
        if len(args_list) < 2:
            write_command(f"say [GIVEMONEY] > {display_username}: Please specify a player and amount, e.g., !givemoney Bob 100")
            press_key()
            return
        recipient = " ".join(args_list[:-1])
        recipient_lower = recipient.lower()
        amount_str = args_list[-1]
        try:
            amount = float(amount_str)
            if amount <= 0:
                write_command(f"say [GIVEMONEY] > {display_username}: Amount must be positive.")
                press_key()
                return
        except ValueError:
            write_command(f"say [GIVEMONEY] > {display_username}: Invalid amount. Use a number, e.g., !givemoney Bob 100")
            press_key()
            return
        if username_lower == recipient_lower:
            write_command(f"say [GIVEMONEY] > {display_username}: You cannot give money to yourself!")
            press_key()
            return
        balances = load_balances()
        player_stats = load_player_stats()
        if recipient_lower not in balances and recipient_lower not in player_stats:
            write_command(f"say [GIVEMONEY] > {display_username}: Player '{recipient}' not found!")
            press_key()
            return
        recipient_display = get_display_username(recipient)
        current_balance = get_balance(username)
        if current_balance < amount:
            write_command(f"say [GIVEMONEY] > {display_username}: Not enough funds! You have ${current_balance:,.2f}, need ${amount:,.2f}")
            press_key()
            return
        update_balance(username, -amount)
        update_balance(recipient, amount)
        write_command(f"say [GIVEMONEY] > {display_username}: You gave ${amount:,.2f} to {recipient_display}! Your new balance: ${round(get_balance(username), 2):,.2f}")
        press_key()
    except Exception as e:
        write_command(f"say [GIVEMONEY] > {display_username}: Error processing transfer. Please try again.")
        press_key()
        logging.error(f"Error in give_money for {username}: {e}")

def commands(username):
    """Display a list of available commands and their descriptions."""
    username_lower = username.lower()
    display_username = get_display_username(username)
    logging.debug(f"Commands requested by {username}")
    command_list = [
        "!gamble",
        "!givemoney"
    ]
    write_command(f"say [COMMANDS] > Available economy commands: {', '.join(command_list)}")
    press_key()
    logging.debug(f"Displayed commands for {username}")
# fork of [galls (a CS2 selfbot)](https://github.com/Pandaptable/galls)

Galls is a somewhat simple python script to generate responses to commands by sending a keystroke (F1) which executes a config file ingame.

## Features
  - fish.
  - more fish.
  - even more fish.
 
### Demo Video (old)

[Demo](https://github.com/Pandaptable/galls/assets/80334807/7a646185-6139-43b3-8f46-de1cdbc64c6c)

## Requirements

- [Python](https://www.python.org/downloads/) only needed if doing manual install

- add `-condebug` to your cs2 launch options (this makes cs log to D:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive\game\csgo\console.log for example.)


## Simple Install
 - grab latest [release](https://github.com/Yizzii/fishbot/releases/latest)
 - extract zip to folder
 - edit the .env file with your username and config paths
 - open CS2GoFish.exe
 - Run `bind f1 yizzibotmessage` in cs2 console

## Manual Install
  - install [Python](https://www.python.org/downloads/)
  - git lone the repo or manually install source into a folder on your computer.
  - cd into repo folder. `cd <path>` in command line
  - run `pip install -r requirements.txt`
  - Run `python main.py` inside of the project directory.
  - Run `bind f1 yizzibotmessage` in cs2 console

## Commands
    "!fish - Cast your line to catch a fish.",
    "!gamble <amount|all|num%> - Gamble money for a 50% chance to double it.",
    "!balance - Check your current balance.",
    "!stats - View your fishing stats (casts, fish caught, rarities).",
    "!globalstats - View global fishing stats (privileged users only).",
    "!givemoney <player> <amount> - Transfer money to another player.",
    "!shop - View rods for purchase.",
    "!shop bait - View baits for purchase.",
    "!shop buy <item_name> - Buy a rod or bait (e.g., Average Rod, Bloodworm).",
    "!commands - Show this list of commands."


## Confused?
  - Q: i can't find yizzibotmessage.cfg where is it?
  -  A: it gets created when you do a command for the first time, you dont need the file when setting its path in .env
  -
  - Q: i can't find console.log where is it?
  - A: you need to add `-condebug` to your cs2 launch options.

## Authors
  - [Yizzi](https://github.com/Yizzii) too many changes.
  - [Pandaptable](https://github.com/Pandaptable) made original galls.
  - [DeaFPS](https://twitter.com/deafps_) for letting me yoink her code and convert it to python... also making the fish database because [fishbase](http://www.fishbase.us/) is way too big.. ly loser <3

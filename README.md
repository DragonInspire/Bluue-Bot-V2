# Bluue-Bot-V2
### Discord Bot for Gathering Guild and Player Data

## Overview
This Discord bot is designed to collect and manage data related to a specific guild and its members in the Wynncraft Minecraft server. It gathers information about the guild's online members and their territories. It also keeps track of war-related data for each player. It is a continuation of <a href="https://github.com/DragonInspire/Bluue-Bot">Bluue-Bot</a> updated to the v3 wynncraft api and better error handling.

## Commands
Blue is built with only one command `/uniform` after which you will be prompted to enter a minecraft username and select a rank `/uniform Username:`.
upon calling the command the bot will send a message containing your minecraft skin with the appropriate farplane uniform.

## Installation

Before using the script, make sure to install the required dependencies listed in the `requirements.txt` file. You can do this using `pip`:

```bash
pip install -r requirements.txt
```
### Alternatively
- Python 3.7+
- Required Python packages (install them using `pip`):
  - `requests`
  - `PIL` (Python Imaging Library)
  - `discord`

## Usage

You can run this discord bot using `python`:

```bash
python bot.py
```

## License
This project is open-source and available under the [MIT License](LICENSE).

## Disclaimer

This script is provided as-is, and its usage is subject to the terms and conditions of the Wynncraft API. Make sure you comply with their API usage guidelines and policies.

## Author

github - DragonInspire <br>
IGN - VainFate

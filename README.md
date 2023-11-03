# Bluue-Bot-V2
### Discord Bot for Gathering Guild and Player Data

## Overview
This Discord bot is designed to collect and manage data related to a specific guild and its members in the Wynncraft Minecraft server. It gathers information about the guild's online members and their territories. It also keeps track of war-related data for each player.

## Installation

Before using the script, make sure to install the required dependencies listed in the `requirements.txt` file. You can do this using `pip`:

```bash
pip install -r requirements.txt
```
### Alternatively
- Python 3.7+
- Required Python packages (install them using `pip`):
  - `requests`
  - `aiohttp`
  - `PIL` (Python Imaging Library)
  - `discord`

## Usage
1. Open a terminal and navigate to the directory containing your bot code.
2. Start the bot by running the appropriate Python script for your desired functionality.

### Bot for Guild and Player Data
- Run the following command to start the bot for gathering guild and player data:
```bash
python guild_data_bot.py
```

- This bot will collect information about online guild members and territories, as well as war-related data.

### Discord Bot for Skin Overlay
- Run the following command to start the bot for overlaying player skins with custom ranks:
```bash
python skin_overlay_bot.py
```

This bot will overlay the skin of a Minecraft player with a specified rank and save the resulting image.

## Bot Descriptions
### Guild Data Bot
- The Guild Data Bot collects information about online guild members, including their in-game username, current world, and rank.
- It also tracks territorial data, recording if the guild has gained or lost territories over time.
- The bot saves this information in JSON files for future analysis.

### Skin Overlay Bot
- The Skin Overlay Bot allows you to overlay a player's Minecraft skin with a custom rank badge.
- It fetches the player's skin and the custom rank badge and combines them into a single image.
- The resulting image is saved as a PNG file for further use.

## Error Handling
The bot is designed with robust error handling to ensure that it continues to function even in the presence of network issues, missing data, or other unexpected problems. It logs errors for debugging purposes.

Please report any issues or bugs to the bot developer.

## License
This project is open-source and available under the [MIT License](LICENSE).

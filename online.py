import requests
import logging
import json

# Configuration
ONLINE_PLAYERS_URL = f"https://api.wynncraft.com/v3/player"

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

class GuildDataException(Exception):
    def __init__(self, message, original_exception=None):
        super().__init__(message)
        self.original_exception = original_exception

class FetchDataException(Exception):
    def __init__(self, message, original_exception=None):
        super().__init__(message)
        self.original_exception = original_exception

def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise FetchDataException(f"Error fetching data from {url}: {e}", original_exception=e)

def get_online_players_with_data():
    online_players_worlds = fetch_data(ONLINE_PLAYERS_URL)
    online_players_worlds.pop("total")
    online_players_worlds = online_players_worlds.get("players")
    online_players = list(online_players_worlds.keys())

    with open("guild_members.json", "r") as file:
        guild_members = json.load(file)

    online_guild_players = [{"player": player.get("player"), "world": online_players_worlds.get(player.get("player")), "rank": player.get("rank") } for player in guild_members if player.get("player") in online_players]

    if not online_guild_players:
        raise GuildDataException("No online players found")

    return online_guild_players
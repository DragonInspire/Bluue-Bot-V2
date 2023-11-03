import requests
import logging

# Configuration
GUILD_NAME = "The Farplane"
GUILD_MEMBERS_URL = f"https://api.wynncraft.com/v3/guild/{GUILD_NAME}"

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    guild_data = fetch_data(GUILD_MEMBERS_URL)
    members = guild_data.get("members", {})

    if "total" in members:
        del members["total"]

    online_players = []

    for rank, rank_data in members.items():
        for player, player_data in rank_data.items():
            if player_data.get("online"):
                world = player_data.get("server")
                online_players.append({"player": player, "world": world, "rank": rank})

    if not online_players:
        raise GuildDataException("No online players found")

    return online_players

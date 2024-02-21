import aiohttp
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

async def fetch_data(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
    except aiohttp.ClientError as e:
        raise FetchDataException(f"Error fetching data from {url}: {e}") from e

async def get_online_players_with_data():
    online_players_worlds = await fetch_data(ONLINE_PLAYERS_URL)
    online_players_worlds.pop("total")
    online_players_worlds = online_players_worlds.get("players")
    online_players = list(online_players_worlds.keys())

    with open("guild_members.json", "r") as file:
        guild_members = json.load(file)

    online_guild_players = [{"player": player.get("player"), "world": online_players_worlds.get(player.get("player")), "rank": player.get("rank") } for player in guild_members if player.get("player") in online_players]

    with open("guild_members_online.json", "w") as file:
        json.dump(online_guild_players, file)

    if not online_guild_players:
        raise GuildDataException("No online players found")

    return online_guild_players
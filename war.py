import requests
#import asyncio
#import aiohttp
import json
import logging

# Configuration
GUILD_NAME = "The Farplane"  # Set the guild name
GUILD_MEMBERS_URL = f"https://api.wynncraft.com/v3/guild/{GUILD_NAME}"  # Guild members API URL
TERRITORIES_URL = 'https://api.wynncraft.com/v3/guild/list/territory'  # Territories API URL

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

# Function to fetch data from a URL using requests library
def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"Error fetching data from {url}: {e}")

# # Asynchronous function to fetch player data using aiohttp
# async def fetch_player_data(player):
#     try:
#         async with aiohttp.ClientSession() as session:
#             async with session.get(f"https://api.wynncraft.com/v3/player/{player}") as response:
#                 response.raise_for_status()
#                 return await response.json()
#     except aiohttp.ClientError as e:
#         raise Exception(f"Error fetching data for {player}: {e}")

# # Asynchronous function to fetch data for a list of players concurrently
# async def get_all_player_data(player_list):
#     tasks = [fetch_player_data(player) for player in player_list]
#     return await asyncio.gather(*tasks)

# Main function
def war_track():
    try:
        # Fetch guild members' data
        members = fetch_data(GUILD_MEMBERS_URL).get("members")
        members.pop("total")  # Remove the "total" key from the members dictionary
        
        # Create a list of online players in the guild
        listOfPlayers = [player for rank in members for player, data in members[rank].items() if data.get("online")]

        # # Initialize an event loop for asynchronous operations
        # loop = asyncio.get_event_loop()
        # # Fetch data for all online players concurrently
        # playerData = loop.run_until_complete(get_all_player_data(listOfPlayers))
 
        playerData = [requests.get(f"https://api.wynncraft.com/v3/player/{player}").json() for player in listOfPlayers]

        # Extract the war counts for online players
        warcountOnlineList = [player.get("globalData").get("wars") for player in playerData]

        # Fetch territory data
        territories = fetch_data(TERRITORIES_URL)

        # Filter territories data for the guild of interest
        teritories_updated = []
        for territory in territories.items():
            if territory[1].get("guild") != None:
                if territory[1].get("guild").get("name") == GUILD_NAME:
                    teritories_updated.append(territory[0])

        # Creates territories.json if it doesnt exist
        with open("territories.json", "a+"):
            pass
            
        try:
            # Load the existing territory data from a JSON file
            with open("territories.json", "r") as old_territories:
                try:
                    data = json.load(old_territories)
                except json.JSONDecodeError as e:
                    logging.error(f"Error loading JSON data: {e}")
                    data = []
                # Check if any new territories were gained
                gained_territory = any(territory not in data for territory in teritories_updated)
        except FileNotFoundError as e:
            # Handle the case where the file doesn't exist
            logging.error(f"File not found: {e}")
        except IOError as e:
            # Handle other input/output errors
            logging.error(f"IO Error: {e}")
        except Exception as e:
            # Handle other exceptions
            logging.error(f"An error occurred: {e}")
        else:
            # This block is executed if no exceptions occur
            logging.debug("File operations completed successfully")
        try:
            # Update the territory data in the JSON file
            with open("territories.json", "w") as old_territories:
                json.dump(teritories_updated, old_territories)
        except FileNotFoundError as e:
            # Handle the case where the file doesn't exist
            logging.error(f"File not found: {e}")
        except IOError as e:
            # Handle other input/output errors
            logging.error(f"IO Error: {e}")
        except Exception as e:
            # Handle other exceptions
            logging.error(f"An error occurred: {e}")
        else:
            # This block is executed if no exceptions occur
            logging.debug("File operations completed successfully")

        # Creates war_data.json if it doesnt exist
        with open("war_data.json", "a+"):
            pass

        try:
            # Load the existing war data from a JSON file
            with open("war_data.json", "r") as storedWarData:
                try:
                    data_1 = json.load(storedWarData)
                except json.JSONDecodeError as e:
                    logging.error(f"Error loading JSON data: {e}")
                    data_1 = {}
                    
                # Update war data for each player
                for i, player in enumerate(listOfPlayers):
                    if player not in data_1:
                        logging.info(f"{player} not in war_data.json")
                        data_1[player] = [0, 0, warcountOnlineList[i]]
                        logging.info(f"{player} added to war_data.json")
                    else:
                        my_data = data_1[player]
                        if my_data[2] != warcountOnlineList[i]:
                            if gained_territory:
                                my_data[0] += 1
                            my_data[1] += warcountOnlineList[i] - data_1[player][2]
                            my_data[2] = warcountOnlineList[i]
                        data_1[player] = my_data
        except FileNotFoundError as e:
            # Handle the case where the file doesn't exist
            logging.error(f"File not found: {e}")
        except IOError as e:
            # Handle other input/output errors
            logging.error(f"IO Error: {e}")
        except Exception as e:
            # Handle other exceptions
            logging.error(f"An error occurred: {e}")
        else:
            # This block is executed if no exceptions occur
            logging.debug("File operations completed successfully")
        
        try:
            # Update the war data in the JSON file
            with open("war_data.json", "w") as storedWarData:
                json.dump(data_1, storedWarData)
        except FileNotFoundError as e:
            # Handle the case where the file doesn't exist
            logging.error(f"File not found: {e}")
        except IOError as e:
            # Handle other input/output errors
            logging.error(f"IO Error: {e}")
        except Exception as e:
            # Handle other exceptions
            logging.error(f"An error occurred: {e}")
        else:
            # This block is executed if no exceptions occur
            logging.debug("File operations completed successfully")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        # Handle the error or raise an exception as needed.

def getWarData():
    with open("war_data.json", "r") as file:
        data = json.load(file)
    return data
import grequests
import json
import logging

# note change the json locations back to ./data/location before pushing to repo

GUILD_NAME = "The Farplane"
GUILD_MEMBERS_URL = f"https://api.wynncraft.com/v3/guild/{GUILD_NAME}"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

async def fetch_data(url_list):
    requests = (grequests.get(url) for url in url_list)
    responses = grequests.map(requests)
    readable_data = []
    for response in responses:
        try:
            if response.status_code == 200:
                data = response.json()
                readable_data.append(data)
            else:
                raise Exception('Request failed with status code:', response.status_code) 
        except Exception as e:
            logging.error(e)
    return readable_data
    
async def track_guild_members():
    new_players = []
    old_players = []
    left_players = []
    try:
        my_response = await fetch_data([GUILD_MEMBERS_URL])
        members = my_response[0].get("members")
        members.pop("total")

        with open("./data/guild_members.json", "r") as file:
            guild_list = json.load(file)

        old_player_list = [player["player"] for player in guild_list]

        player_list = []
        for rank, rank_data in members.items():
            for player, player_data in rank_data.items():
                world = player_data.get("server")
                player_list.append({"player": player, "world": world, "rank": rank})
                if player in old_player_list:
                    old_players.append(player)
                else:
                    new_players.append(player)   

        with open("./data/guild_members.json", "w") as file:             
            json.dump(player_list, file)

        for my_player in old_player_list:
            if my_player not in old_players and my_player not in new_players:
                left_players.append(my_player)

        return {"newPlayers": new_players, "leftPlayers": left_players}
        
    except Exception as e:
        logging.error(e)
    
    

async def level_tracking():
    with open("./data/guild_members.json", "r") as file:
        guild_list = json.load(file)
    
    my_player_list = [player["player"] for player in guild_list]
    my_urls = [f"https://api.wynncraft.com/v3/player/{player}?fullResult" for player in my_player_list]
    player_data_list = await fetch_data(my_urls)

    prof_milestones = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130]
    player_milestones = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 103, 105, 106]
    
    level_ups = []

    with open("./data/player_data.json", "r") as file:
        stored_player_data = json.load(file)

    player_class_levels = []
    for player in player_data_list:
        try:
            player_data = player
            characters = player_data["characters"]
            for characteruuid in characters:
                level = characters[characteruuid]["level"]
                level_name = characters[characteruuid]["type"]
                my_dict = {"usermame": player["username"], "uuid": characteruuid, "level": level, "class": level_name}
                professions = characters[characteruuid]["professions"]
                for stored_class in stored_player_data:
                    if stored_class["uuid"] == characteruuid:
                        for milestone in player_milestones:
                            if level >= milestone and stored_class["level"] < milestone:
                                level_ups.append({"username": player["username"], "class": characters[characteruuid]["type"], "type": "combat", "milestone": milestone})
                        for profession in professions:
                            for milestone in prof_milestones:
                                if professions[profession]["level"] >= level and stored_class[profession] < level:
                                    level_ups.append({"username": player["username"], "class": characters[characteruuid]["type"], "type": profession, "milestone": milestone})
                for profession in professions:
                    my_dict[profession] = professions[profession]["level"]
                player_class_levels.append(my_dict)
        except Exception as e: 
            logging.error(e)

    with open("./data/player_data.json", "w") as file:
        json.dump(player_class_levels, file)
    
    return level_ups

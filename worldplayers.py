from online import fetch_data
def world_players(world):
    API_URL=f"https://beta-api.wynncraft.com/v3/player?server={world}"
    reply = await fetch_data(API_URL)

    players = reply["players"]

    player_list = [key for key in players]


    players_data = []
    for player in player_list:
        player_data = await fetch_data(f"https://beta-api.wynncraft.com/v3/player/{player}?fullResult")
        try:
            guild = player_data["guild"]["name"]
        except:
            guild = "No Guild"
        try:
            characters = player_data["characters"]
            highest_level = 0
            for characteruuid in characters:
                if characters[characteruuid]["level"] > highest_level:
                    highest_level = characters[characteruuid]["level"]
                    highest_level_name = characters[characteruuid]["type"]
        except: 
            highest_level = 0
            highest_level_name = "No Characters"


        players_data.append([player, guild, highest_level_name, highest_level])


    return players_data

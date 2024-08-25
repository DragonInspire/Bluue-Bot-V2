from online import fetch_data
async def world_players(world):
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
            guild = "None"
        try:
            characters = player_data["characters"]
            highest_level = 0
            for characteruuid in characters:
                if characters[characteruuid]["level"] > highest_level:
                    highest_level = characters[characteruuid]["level"]
                    highest_level_name = characters[characteruuid]["type"]
        except: 
            highest_level = 0
            highest_level_name = "None"


        players_data.append([player, guild, highest_level_name, highest_level])

    null_sorted_list = []
    for player in player_data:
        if player[1] == "none":
            null_sorted_list.append(player)

    null_sorted_list = sorted(null_sorted_list, key = lambda player: player[3])
    for player in player_data:
        if player[1] != "none":
            null_sorted_list.append(player)


    return players_data

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
            rank = player_data["rank"]
            firstjoin = player_data["firstJoin"]
            highest_level = 0
            for characteruuid in characters:
                if characters[characteruuid]["level"] > highest_level:
                    highest_level = characters[characteruuid]["level"]
                    highest_level_name = characters[characteruuid]["type"]
        except: 
            highest_level = 0
            highest_level_name = "None"


        players_data.append([player, guild, highest_level_name, highest_level, rank, firstjoin])

    null_sorted_list = []
    for player in players_data:
        if player[1] == "None":
            null_sorted_list.append(player)

    null_sorted_list = sorted(null_sorted_list, key = lambda player: player[3])
    for player in players_data:
        if player[1] != "None":
            null_sorted_list.append(player)


    return null_sorted_list

import json
from war import fetch_data, GUILD_MEMBERS_URL

def contributions():
    members = fetch_data(GUILD_MEMBERS_URL).get("members")
    members.pop("total")  # Remove the "total" key from the members dictionary

    list_of_xp_contributions = {}
    for rank in members:
        for player in members[rank]:
            name = player
            xp = members[rank][player].get("contributed")
            list_of_xp_contributions[name] = xp

    with open("./data/guild_members_xp.json", "r") as file:
        old_list_of_xp_contributions = json.load(file)

    for player in list_of_xp_contributions:
        try:
            old_list_of_xp_contributions[player]
        except:
            old_list_of_xp_contributions[player] = 0

    change = [{player:(list_of_xp_contributions[player] - old_list_of_xp_contributions[player])} for rank in members for player in members[rank] ]

    with open("./data/guild_members_xp.json", "w") as file:
        json.dump(list_of_xp_contributions, file)

    top_10 = {}
    for player in change:
        if list(player.values())[0] != 0:
            top_10[list(player.keys())[0]] = list(player.values())[0]

    return(top_10)

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

    with open("guild_members_xp.json", "r") as file:
        old_list_of_xp_contributions = json.load(file)

    change = [{player:(list_of_xp_contributions[player] - old_list_of_xp_contributions[player])} for rank in members  for player in members[rank] ]

    with open("guild_members_xp.json", "w") as file:
        json.dump(list_of_xp_contributions, file)

    object_change = {}
    for key in change:
        if change[key] != 0:
            object_change[key] = change[key]

    return(object_change)
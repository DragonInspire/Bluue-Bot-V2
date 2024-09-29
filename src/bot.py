import typing
from discord.ext import commands, tasks
import discord
import logging
from discord import app_commands
from discord.ui import Select, View
from uniform import overlay_images, get_head
from online import get_online_players_with_data, FetchDataException, GuildDataException, fetch_data
#from war import war_track, getWarData
from xp_tracking import contributions
from dotenv import load_dotenv
import os
from wynntils_parse import decode_item
import zaibatsu
from molah import invest, withdraw, getInvestments, emeraldTypesToEmeralds, parsePrice, getProfit
import random
from mythicImage import mythicImage
from worldplayers import world_players
from io import StringIO
from datetime import datetime
from levelTracking import track_guild_members, level_tracking
import requests

devFlag = False

# Logging setup
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

# Load environment variables from a .env file
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

if (not devFlag):
    XP_LEADERBOARD_CHANNEL_ID = int(os.getenv('XP_LEADERBOARD_CHANNEL_ID'))
    ONLINE_PLAYER_CHANNEL = int(os.getenv('ONLINE_PLAYER_CHANNEL'))
    # ONLINE_PLAYER_MESSAGE = int(os.getenv('ONLINE_PLAYER_MESSAGE'))


# Initialize the bot

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

zaibatsu_group = app_commands.Group(name="zaibatsu", description="mythic bank related commands")
bot.tree.add_command(zaibatsu_group)
farplane_group = app_commands.Group(name="farplane", description="the farplane related commands")
bot.tree.add_command(farplane_group)

# Event: Bot is ready
@bot.event
async def on_ready():
    logging.info("Bot is running")
    try:
        # Attempt to sync the commands with the server
        synced = await bot.tree.sync()
        for synced_command in synced:
            logging.info(f"Synced {synced_command} command")
    except Exception as e:
        logging.error(e)

    # Start background tasks
    try:
        if not change_status.is_running():
            change_status.start()
            logging.info("status update task started")
        else:
            logging.info("status update already started")
        if not farplane_online.is_running() and not devFlag:
            farplane_online.start()
            logging.info("Farplane online task started")
        else:
            logging.info("farplane online already started")

        if not leveling.is_running() and not devFlag:
            leveling.start()
            logging.info("leveling started")
        else:
            logging.info("leveling already started")
        # if not war_tracking.is_running() and not devFlag:
        #     war_tracking.start()
        #     logging.info("War tracking task started")
        # else:
        #     logging.info("war tracking already started")
        # '''
        # if not war_update.is_running():
        #     war_update.start()
        #     logging.info("War update task started")
        # else:
        #     logging.info("war update already started")
        # '''
        if not xp_leaderboard.is_running() and not devFlag:
            xp_leaderboard.start()
            logging.info("xp leaderboard task started")
        else:
            logging.info("xp leaderboard already running")
    except Exception as e:
        logging.exception(f"unhandled exception while starting tasks {e}")
@zaibatsu_group.command(name="invest")
@app_commands.describe(player_name="player name: ")
@app_commands.describe(amount="stack and le invest #stx #le: ")
async def zaibatsu_invest(interaction: discord.Interaction, player_name: str, amount: typing.Optional[str] = "0"):
    try:
        invest(player_name.lower(), amount.lower())
        await interaction.response.send_message(f"{player_name} investment of {amount} sucessful")
    except Exception as e:
        logging.info(e)
        raise e
        await interaction.response.send_message(f"{player_name} investment of {amount} failed")
        
@zaibatsu_group.command(name="withdraw")
@app_commands.describe(player_name="player name: ")
@app_commands.describe(amount="stack and le invest #stx #le: ")
async def zaibatsu_withdraw(interaction: discord.Interaction, player_name: str, amount: typing.Optional[str] = "0"):
    try:
        withdraw(player_name.lower(), amount.lower())
        await interaction.response.send_message(f"{player_name} withdraw of {amount} sucessful")
    except Exception as e:
        logging.info(e)
        await interaction.response.send_message(f"{player_name} withdraw of {amount} failed")    

@zaibatsu_group.command(name="addfrozen")
@app_commands.describe(player_name="player name: ")
@app_commands.describe(amount="stack and le invest #stx #le: ")
async def zaibatsu_addfrozen(interaction: discord.Interaction, player_name: str, amount: typing.Optional[str] = "0"):
    try:
        invest(player_name.lower(), amount.lower(), categories=("frozen", "initial"))
        await interaction.response.send_message(f"{player_name} addfrozen of {amount} sucessful")
    except Exception as e:
        logging.info(e)
        await interaction.response.send_message(f"{player_name} addfrozen of {amount} failed")

@zaibatsu_group.command(name="rmfrozen")
@app_commands.describe(player_name="player name: ")
@app_commands.describe(amount="stack and le invest #stx #le: ")
async def zaibatsu_rmfrozen(interaction: discord.Interaction, player_name: str, amount: typing.Optional[str] = "0"):
    try:
        withdraw(player_name.lower(), amount.lower(), categories=("frozen", "initial"))
        await interaction.response.send_message(f"{player_name} rmfrozen of {amount} sucessful")
    except Exception as e:
        logging.info(e)
        await interaction.response.send_message(f"{player_name} rmfrozen of {amount} failed")

@zaibatsu_group.command(name="investmentlist")
async def zaibatsu_investment_list(interaction: discord.Interaction, raw: typing.Optional[bool] = False, frozen: typing.Optional[bool] = False, initial: typing.Optional[bool] = False, profit: typing.Optional[bool] = False):
    #try:

    cat = "raw"
    colour = discord.Colour.dark_teal()
    img_link = mythicImage("Raw")
    if raw:
        cat = "raw"
    elif frozen:
        cat = "frozen"
        colour = discord.Colour.dark_purple()
        img_link = mythicImage("UNID")
    elif initial:
        cat = "initial"
        colour = discord.Colour.dark_blue()

    if profit:
        cat = "profit"
        img_link = mythicImage("GoldRaw")
        colour = discord.Colour.dark_gold()
        investments = getProfit()
    else:
        investments = getInvestments(cat)

    embed=discord.Embed(
        colour = colour,
        title = f"Mythic Bank Investments {cat}"
    )
    embed.set_thumbnail(url=img_link)
    
    for player in investments.keys():
        embed.add_field(name=player, value=investments[player])

    await interaction.response.send_message(embed=embed)
    #except Exception as e:
    #    await interaction.response.send_message("list failed")
    #    logging.info(e)
    


@zaibatsu_group.command(name="buy")
@app_commands.describe(mythic_name="mythicName:")
@app_commands.describe(player_name="playerName:")
@app_commands.describe(overall="item percent or other unique id")
@app_commands.describe(cost="cost of buying 0 if looted")
@app_commands.describe(status="in bank out of bank or other")
@app_commands.describe(notes="anything else")
@app_commands.describe(wynntils="wynntils string")
async def zaibatsu_buy(interaction: discord.Interaction, mythic_name: str, player_name: str, overall: typing.Optional[str] = "", 
                          cost: typing.Optional[str] = "0", status: typing.Optional[str] = "bank",
                           notes: typing.Optional[str] = "", wynntils: typing.Optional[str] = ""):
    out = zaibatsu.bought(player_name.lower(), 
                          mythic_name.lower(), 
                          overall=overall.lower(), 
                          cost=cost.lower(), 
                          status=status.lower(), 
                          notes=notes, wynntils=wynntils)
    await interaction.response.send_message(out)

@zaibatsu_group.command(name="update")
@app_commands.describe(mythic_name="mythicName:")
@app_commands.describe(player_name="playerName:")
@app_commands.describe(overall="item percent or other unique id")
@app_commands.describe(cost="cost of buying 0 if looted")
@app_commands.describe(status="in bank out of bank or other")
@app_commands.describe(notes="anything else")
@app_commands.describe(wynntils="wynntils string")
async def zaibatsu_update(interaction: discord.Interaction, mythic_name: str, player_name: str, overall: typing.Optional[str] = "", 
                          cost: typing.Optional[str] = None, status: typing.Optional[str] = None,
                           notes: typing.Optional[str] = None, wynntils: typing.Optional[str] = None):
    out = zaibatsu.update(player_name.lower(), 
                          mythic_name.lower(), 
                          overall=overall.lower(), 
                          cost=cost.lower(), 
                          status=status.lower(), 
                          notes=notes, wynntils=wynntils)
    await interaction.response.send_message(out)

@zaibatsu_group.command(name="rename")
@app_commands.describe(mythic_name="mythicName:")
@app_commands.describe(player_name="playerName:")
@app_commands.describe(overall="item percent or other unique id")
@app_commands.describe(new_mythic_name="playerName:")
@app_commands.describe(new_player_name="playerName:")
@app_commands.describe(new_overall="item percent or other unique id")
async def zaibatsu_rename(interaction: discord.Interaction, mythic_name: str, player_name: str, overall: typing.Optional[str] = "", 
                new_mythic_name: typing.Optional[str] = None, new_player_name: typing.Optional[str] = None, new_overall: typing.Optional[str] = None):
    # can't use lower if its None, and None is different from empty string here in that it doesn't reassign the existing value
    if new_mythic_name is not None:
        new_mythic_name = new_mythic_name.lower()
    if new_player_name is not None:
        new_player_name = new_player_name.lower()
    if new_overall is not None:
        new_overall = new_overall.lower()
    out = zaibatsu.rename(player_name.lower(),
                          mythic_name.lower(),
                          overall=overall.lower(),
                          new_mythic_name=new_mythic_name,
                          new_player_name=new_player_name,
                          new_overall=new_overall)
    await interaction.response.send_message(out)

@zaibatsu_group.command(name="sell")
@app_commands.describe(mythic_name="mythicName:")
@app_commands.describe(player_name="playerName:")
@app_commands.describe(overall="item percent or other unique id")
@app_commands.describe(price="sell price")
async def zaibatsu_sell(interaction: discord.Interaction, mythic_name: str, player_name: str, overall: typing.Optional[str] = "", 
                          price: typing.Optional[str] = "0"):
    out = zaibatsu.sold(player_name.lower(), mythic_name.lower(), overall=overall.lower(), price=price.lower())
    await interaction.response.send_message(out)

@zaibatsu_group.command(name="view")
@app_commands.describe(mythic_name="mythicName:")
@app_commands.describe(player_name="playerName:")
@app_commands.describe(overall="item percent or other unique id")
async def zaibatsu_view(interaction: discord.Interaction, mythic_name: str, player_name: str, overall: typing.Optional[str] = ""):
    out = zaibatsu.view(player_name.lower(), mythic_name.lower(), overall=overall.lower())
    await interaction.response.send_message(out)

async def interaction_respond_or_follow(interaction: discord.Interaction, message):
    responded = interaction.response.is_done()
    if not responded:
        await interaction.response.send_message(message)
    else:
        await interaction.followup.send(content=message)

@zaibatsu_group.command(name="list")
@app_commands.describe(detailed="include data fields")
async def zaibatsu_list(interaction: discord.Interaction, detailed: typing.Optional[bool] = False):
    # embed = discord.Embed(
    #     colour = discord.Colour.purple(),
    #     title = "Mythic Bank"
    # )
    # embed.set_thumbnail(url="https://www.wynndata.tk/assets/images/items/v4/unidentified/mythic.png")
    # mythic_list = zaibatsu.listBank(detailed=detailed)
    # for player in mythic_list.keys():
    #     embed.add_field(name=player, value=mythic_list[player], inline=False)
    # embed.set_footer(text="be sure to include overall when using specific commands")
    # await interaction.response.send_message(embed=embed)
    message = "```"
    message += "Mythic Bank"
    message += "\n"
    msg_rows = 1
    max_msg_rows = 10 if detailed else 30
    mythic_list = zaibatsu.listBank(detailed=detailed)
    for player in mythic_list.keys():
        message += str(player) + " " + str(mythic_list[player]) + "\n"
        msg_rows += 1
        if msg_rows >= max_msg_rows:
            message += "```"
            await interaction_respond_or_follow(interaction, message)
            message = "```"
            msg_rows = 0

    message += "\nBe sure to include overall when using specific commands"
    message += "```"
    await interaction_respond_or_follow(interaction, message)
    

@zaibatsu_group.command(name="display")
@app_commands.describe(mythic_name="mythicName:")
@app_commands.describe(player_name="playerName:")
@app_commands.describe(overall="item percent or other unique id")
@app_commands.describe(nori_command="check weigh pricecheck or any other nori command that takes wynntils string")
async def zaibatsu_display(interaction: discord.Interaction, mythic_name: str, player_name: str, overall: typing.Optional[str] = "", nori_command: typing.Optional[str] = "weigh"):
    try:
        wynntils = zaibatsu.getWynntils(player_name.lower(), mythic_name.lower(), overall=overall.lower())
    except:
        await interaction.response.send_message("item not in mythic bank, make sure to be exact")
        return
    try:
        decoded_item = decode_item(wynntils)
        name = decoded_item.name
        try:
            api_request = await fetch_data(f"https://api.wynncraft.com/v3/item/search/{name}")
            api_ids = api_request[name]["identifications"]
        except Exception as e:
            await interaction.response.send_message("error fetching item from wynntils api")
            logging.info(e)
            return
        
        ids = {}
        for id in decoded_item.identifications:
            ids[id.id] = id.value    

        ids_percents = {}
        for key in ids.keys():
            values = api_ids[key]
            if (type(values)) != type(1):
                min = values["min"]
                max = values["max"]
                difference = max - min
                value = ids[key]
                value = value-min
                try:
                    percent = value/difference
                    ids_percents[key] = round(percent * 100)
                except ZeroDivisionError:
                    ids_percents[key] = ""
            else:
                ids_percents[key] = ""
        powder = decoded_item.powder
        rerolls = decoded_item.reroll

        embed = discord.Embed(
            colour = discord.Colour.dark_magenta(),
            title = name
        )
        embed.set_thumbnail(url=mythicImage(name))
        embed.set_footer(text="owned by: " + player_name)

        for id in ids.keys():
            if type(ids_percents[id]) == type(1):
                embed.add_field (name = str(id), value = str(ids[id]) + " (" + str(ids_percents[id]) + "%)")
            else:
                 embed.add_field (name = str(id), value = str(ids[id]))
        embed.add_field(name = "powders: ", value = str(powder), inline = False)
        embed.add_field(name = "rerolls: ", value = str(rerolls), inline = False)
        await interaction.response.send_message(embed=embed)
    except ValueError as e: 
        out = "wynntils string out of date"
        await interaction.response.send_message(out)
    except Exception as e:
        out = "something went wrong"
        logging.error(e)
        await interaction.response.send_message(out)
        
    

@zaibatsu_group.command(name="wynntils")
@app_commands.describe(mythic_name="mythicName:")
@app_commands.describe(player_name="playerName:")
@app_commands.describe(overall="item percent or other unique id")
async def zaibatsu_wynntils(interaction: discord.Interaction, mythic_name: str, player_name: str, overall: typing.Optional[str] = ""):
    try:
        wynntils = zaibatsu.getWynntils(player_name, mythic_name, overall=overall)
        await interaction.response.send_message(f"{wynntils}")
    except:
        await interaction.response.send_message("mythic not in mythic bank")

# Command: Display help information
@bot.tree.command(name="help")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(
        colour = discord.Colour.blue(),
        title = "commands"
    )
    embed.add_field(name="/help", value="shows this list", inline=False)
    embed.add_field(name="/farplane uniform", value = "your minecraft skin with your farplane uniform!", inline=False)
    embed.add_field(name="/farplane pocketbook", value = "see the farplane pocketbook with useful information!", inline=False)
    embed.add_field(name="/farplane cape", value = "get the farplane wynntils cape!", inline=False)
    embed.add_field(name="/farplane animatedcape", value = "get the animated farplane cape for use by wynntils donators!", inline=False)
    embed.add_field(name="/farplane excursioncape", value = "get the farplane excursion animated cape for use by wynntils donators!", inline=False)
    embed.add_field(name="/farplane timeline", value = "get to know the history of the farplane guild with some dramatic flair", inline=False)
    embed.add_field(name="/farplane signature", value = "get the farplane signature for use on the wynncraft forums", inline=False)
    embed.add_field(name="/zaibatsu buy", value = "add a mythic to the mythic bank", inline=False)
    embed.add_field(name="/zaibatsu update", value="updates a mythic in the mythic bank", inline=False)
    embed.add_field(name="/zaibatsu rename", value="changes owner, name, overall for a mythic in the mythic bank", inline=False)
    embed.add_field(name="/zaibatsu sell", value="remove a mythic from the mythic bank", inline=False)
    embed.add_field(name="/zaibatsu view", value="view the data of a mythic in the mythic bank", inline=False)
    embed.add_field(name="/zaibatsu display", value="view the stats of a mythic if it has a saved wynntils string", inline=False)
    embed.add_field(name="/zaibatsu list", value="view all mythics in the bank", inline=False)
    embed.add_field(name="/zaibatsu invest", value="invest emeralds in the mythic bank", inline=False)
    embed.add_field(name="/zaibatsu withdraw", value ="withdraw emeralds from the mythic bank", inline=False)
    embed.add_field(name="/zaibatsu investmentlist", value="lists all emerald investments in the mythic bank", inline=False)
    
    
    await interaction.response.send_message(embed=embed)

@farplane_group.command(name="animatedcape")
async def animatedcape(interaction: discord.Interaction):
    await interaction.response.send_message("https://media.discordapp.net/attachments/1289229656666406924/1289995416359669845/farplane_cape.gif?ex=66fad95a&is=66f987da&hm=63d3cf28137564d13acec7f9433613ae58e879baf5769278ced0b77e3961daca&=")

@farplane_group.command(name="cape")
async def cape(interaction: discord.Interaction):
    await interaction.response.send_message("https://media.discordapp.net/attachments/1289229656666406924/1289995359866720266/BM9zG6u.png?ex=66fad94c&is=66f987cc&hm=b61e927b519ebf3f3a68dc4b0479fbd1252b2e187a1e996af8ba626b36f95a4d&=&format=webp&quality=lossless")

@farplane_group.command(name="excursioncape")
async def excursioncape(interaction: discord.Interaction):
    await interaction.response.send_message("https://media.discordapp.net/attachments/1289229656666406924/1289995392896729211/excursion_cape.gif?ex=66fad954&is=66f987d4&hm=157949db84bb43ea89ad4821a01cf16e3a13e92993b20d3648404625510f39f9&=")

@farplane_group.command(name="pocketbook")
async def pocketbook(interaction: discord.Interaction):
    await interaction.response.send_message("https://drive.google.com/file/d/11UyguBCkemsKOKTyn3LrpT81HnxHwFDK/view")

@farplane_group.command(name="timeline")
async def timeline(interaction: discord.Interaction):
    await interaction.response.send_message("https://docs.google.com/document/d/1KtCntwPyaEaaEe8VVc3a-_pmuV6argoi2m2gun53EDE/edit")

@farplane_group.command(name="signature")
async def signature(interaction: discord.Interaction, year: typing.Literal["2020", "2021", "2022", "2023"]):
    years = ["2020": "https://media.discordapp.net/attachments/1289229656666406924/1290001922547257405/farplane2020.gif?ex=66fadf69&is=66f98de9&hm=0804ae573967656f0ee42fd82f89acc3a03bebf6e05c11cc0fe5e7cab71d8807&=",
            "2021": "https://media.discordapp.net/attachments/1289229656666406924/1290001945938886770/farplane2021.gif?ex=66fadf6e&is=66f98dee&hm=c693de21c6d1fec40b06cfa3245d407ddbf767e8cf567a8199cb6d93fbde6b53&=",
            "2022": "https://media.discordapp.net/attachments/1289229656666406924/1290001969695555644/farplane2022signature.gif?ex=66fadf74&is=66f98df4&hm=c44a6dc6ad96acae13c8ece0c8cc35bfbc4b3ece750916297a01ebe691189f92&=",
            "2023": "https://media.discordapp.net/attachments/1289229656666406924/1290001993758408764/farplane2023signature.gif?ex=66fadf7a&is=66f98dfa&hm=a43c76e834fb7a4bbf8d60842a62c6c3f97d190bbc9192711b85c9a9739ccd6b&="]
    try:
        await interaction.response.send_message(f"Here is the {year}, forum signature" + years[year])
    except:
        await interaction.response.send_message(f"{year} does not have a farplane forum signature")

# Command: Choose a uniform rank
@farplane_group.command(name="uniform")
@app_commands.describe(username="Username:")
async def uniform(interaction: discord.Interaction, username: str, rank: typing.Literal["resident", "buke", "bushi", "shogun", "yako"]):
    try:
        file = discord.File(overlay_images(username, rank), filename="uniform.png")
        await interaction.response.send_message(f"Hey {username}, here is your {rank} uniform", file=file)
    except:
        await interaction.response.send_message(f"sorry either {username} or {rank} were invalid please check your capitalization.")


@bot.tree.command(name="wc")
@app_commands.describe(world="world: ")
async def wc(interaction: discord.Interaction, world: str):
    channel = interaction.channel
    await interaction.response.send_message("request acknowledged please wait")
    the_world_players = await world_players(world)

    message = f" \t  \t  Players online on WC{world}"
    
    for player in the_world_players:
        message += "\n" + str(player[0]) + " "*(18-len(player[0])) + " " + str(player[1]) + " "*(30-len(player[1]))  + str(player[2]) + " "*(10-len(player[2])) + str(player[3]) + " "*(4-len(str(player[3])))  + str(player[4]) + " "*(10-len(player[4])) +  str(player[5])

    buffer = StringIO(message)
    f = discord.File(buffer, filename="playersonline.txt")
        
    await channel.send(file = f)
        

# Background task: Fetch and display online players
@tasks.loop(seconds=30)
async def farplane_online():
    channel = None
    try:
        try:
            channel = bot.get_channel(ONLINE_PLAYER_CHANNEL)
            #message = await channel.fetch_message(ONLINE_PLAYER_MESSAGE)
        except (discord.Forbidden, discord.NotFound) as e:
            logging.error(f"Error: Failed to get channel or message. {e}")
            return
        
        if channel is None:
            return

        try:
            online_peoples = await get_online_players_with_data()
        except FetchDataException as e:
            logging.error(f"Error: Failed to get online players from Wynncraft API. {e}")

            messages = []
            async for message in channel.history(limit=200):
                messages.append(message)
            for message in messages:
                if message.author == bot.user:
                    await message.delete()
            embed = discord.Embed(
                colour = discord.Colour.blue(),
                title = "Failed to get online players from the Wynncraft API."
            )
            await channel.send(embed = embed)
            return
        
        except GuildDataException as e:
            logging.debug(f"No online players found {e}")
            messages = []
            async for message in channel.history(limit=200):
                messages.append(message)
            for message in messages:
                if message.author != bot.user:
                    pass
                else:
                    await message.delete()
            embed = discord.Embed(
                colour = discord.Colour.blue(),
                title = "Online members of The Farplane guild"
            )
            embed.add_field(name = "no players online", value = "")
            await channel.send(embed = embed)
            return

        # nothing went wrong somehow
        messages = []
        async for message in channel.history(limit=200):
            messages.append(message)
        for message in messages:
            if message.author != bot.user:
                pass
            else:
                await message.delete()

        embed = discord.Embed(
            colour = discord.Colour.blue(),
            title = "Online members of The Farplane guild"
        )

        # Create a dictionary to group players by their worlds
        world_players = {}

        for item in online_peoples:
            world = item["world"]
            player = item["player"]
            rank = item["rank"]

            if world not in world_players:
                world_players[world] = []

            world_players[world].append({"rank": rank, "player": player})

            sorted_worlds = sorted(world_players)

            new_list = [world_players[world] for world in sorted_worlds]
            world_players = dict(zip(sorted_worlds, new_list))

        temp_message = ""
        # Iterate through the dictionary and print the players in each world
        for world, players in world_players.items():
            for player_data in players:
                temp_message += (f'{player_data["rank"]}: {player_data["player"]}' + "\n")
            embed.add_field(name = f'World {world}', value = temp_message, inline = False)
            temp_message = ""

        await channel.send(embed = embed)
    except Exception as e:
        logging.exception(f"unhandled exception in farplane online {e}")

# # Background task: Track wars
# @tasks.loop(minutes=10)
# async def war_tracking():
#     try:
#         war_track()
#     except Exception as e:
#         logging.error(f"unhandled exception in war tracking {e}")
# '''
# # Background task: Update war data
# @tasks.loop(minutes=10)
# async def war_update():
#     try:
#         try:
#             channel = bot.get_channel(1131996950548467782)  # Need to send a message to update
#             message = await channel.fetch_message(1170050710948294687)
#         except (discord.Forbidden, discord.NotFound) as e:
#             logging.error(f"Error: Failed to get channel or message. {e}")
#             return
        
#         try:
#             data = getWarData()
#         except FileNotFoundError as e:
#             # Handle the case where the file doesn't exist
#             logging.error(f"File not found: {e}")
#             await message.edit(content="Error: File not found")
#             return
#         except IOError as e:
#             # Handle other input/output errors
#             logging.error(f"IO Error: {e}")
#             await message.edit(content="Error: Output error from file")
#             return
#         except Exception as e:
#             # Handle other exceptions
#             logging.error(f"An error occurred: {e}")
#             await message.edit(content="Error: An unknown error occurred")
#         else:
#             # This block is executed if no exceptions occur
#             logging.debug("File operations completed successfully")

#         sorted_data = sorted(data, key=lambda x: x[1][0])
#         if len(sorted_data) > 10:
#             sorted_data = sorted_data[:10]
        
#         printable_message = "**Farplane War Leaderboard**$```$"

#         for player in sorted_data:
#             printable_message += player
#             printable_message += f" | successful wars {data[player][0]} | " 
#             printable_message += f"total wars {data[player][1]}$"
        
#         printable_message += f"```$Last update at {datetime.now()} UTC time"
#         printable_message = printable_message.replace("$", "\n")
#         await message.edit(content=printable_message)
#     except Exception as e:
#         logging.exception(f"unhandled exception in war update {e}")
# '''

@tasks.loop(minutes=1)
async def leveling():
    channel = bot.get_channel(XP_LEADERBOARD_CHANNEL_ID)
    now = datetime.now()
    emoji_map = {"wand": "<:wand:1289276211863879791>", "tailoring": "<:tailoring:1289276201931636766>", "spear": "<:spear:1289276191852859413>", "scribing" :"<:scribing:1289276181539065908>", "relik":"<:relik:1289276166523457578>", "mining":"<:mining:1289276156092088433>", "jeweling": "<:jeweling:1289276145342218301>", "fishing": "<:fishing:1289276135963889815>", "dagger": "<:dagger:1289276105970421814>", "cooking": "<:cooking:1289276095295787028>", "combat": "<:combat:1289417934623473705>", "bow" : "<:bow:1289276073296527450>", "armoring": "<:armoring:1289276062664228906>", "alchemism": "<:alchemism:1289276044049776720>", "farming": "<:farming:1289276124630749204>", "woodcutting": "<:woodcutting:1289281582452183211>", "woodworking": "<:woodworking:1289281594078531627>", "weponsmithing": "<:weponsmithing:1289281605621256253>"}
    if now.minute % 2 == 0:
        try:
            level_ups = await level_tracking() # {"username": <username>, "class": <class>, "type": <type>, "milestone": <level>}
            for level_up in level_ups:
                embed = discord.Embed(colour = discord.Colour.blurple())
                username = str(level_up["username"])
                level_type = str(level_up["type"])
                milestone = int(level_up["milestone"])
                level_class = str(level_up["class"]).lower()
                if level_class == "mage" or level_class == "darkwizard":
                    class_image = emoji_map["wand"]
                if level_class == "warrior" or level_class == "knight":
                    class_image = emoji_map["spear"]
                if level_class == "archer" or level_class == "hunter":
                    class_image = emoji_map["bow"]
                if level_class == "assassin" or level_class == "ninja":
                    class_image = emoji_map["dagger"]
                if level_class == "shaman" or level_class == "skyseer":
                    class_image = emoji_map["relik"]
                file = discord.File(fp = get_head(username), filename=f"{username}_head.png")
                embed.add_field(name = username, value = f"has reached {emoji_map[level_type.lower()]} {milestone} on {class_image} :tada:", inline = False)
                embed.set_thumbnail(url=f"attachment://{username}_head.png")
                await channel.send(embed=embed, file=file)
        except Exception as e:
            logging.error("EVEN MORE BAD THINGS HAPPENED levelups is " + str(level_ups) + " " + str(e))
    if now.minute % 10 == 0:
        try: 
            player_update = await track_guild_members()
            new_players = player_update["newPlayers"]
            left_players = player_update["leftPlayers"]
            guild_levelup = player_update["guildLevelup"]
            for player in new_players:
                embed = discord.Embed(colour = discord.Colour.blurple())
                file = discord.File(fp = get_head(player), filename=f"{player}_head.png")
                embed.add_field(name = player, value = "has joined the guild!")
                embed.set_thumbnail(url=f"attachment://{player}_head.png")
                await channel.send(embed=embed, file=file)
            for player in left_players:
                embed = discord.Embed(colour = discord.Colour.blurple())
                file = discord.File(fp = get_head(player), filename=f"{player}_head.png")
                embed.add_field(name = player, value = "has left the guild!")
                embed.set_thumbnail(url=f"attachment://{player}_head.png")
                await channel.send(embed=embed, file=file)
            if guild_levelup != -1:
                embed = discord.Embed(colour = discord.Colour.blurple())
                embed.add_field(name = "The Farplane", value = f"has leveled up to level {guild_levelup}! :tada:")
                channel.send(embed=embed)
        except Exception as e:
            logging.error("BAD THINGS HAPPENED player update is " + str(player_update) + " " + str(e))
    

@tasks.loop(minutes=1)
async def xp_leaderboard():
    now = datetime.now()
    if now.hour != 4:
        return
    if now.minute != 0:
        return
    try:
        daily_contributions = contributions()
        if len(daily_contributions) == 0:
            return
        daily_contributions = dict(reversed(sorted(daily_contributions.items(), key=lambda item: item[1])))
        list_10 = {}
        for i, key in enumerate(daily_contributions):
            if i > 9:
                break

            list_10[key] = daily_contributions[key]
        
        channel = bot.get_channel(XP_LEADERBOARD_CHANNEL_ID)
        embed = discord.Embed(
            colour = discord.Colour.blue(),
            title = "Farplane daily top 10 XP Contributions"
        )
        for player in list_10:
            embed.add_field(name = player, value = f"{list_10[player]:,}", inline = False)
        await channel.send(embed=embed)
    except Exception as e:
        logging.exception(f"unhandled exception in xp leaderboard {e}")

@tasks.loop(minutes=1)
async def change_status():
    messages = ["/uniform", "/zaibatsu", "/wc"]
    choice = random.choice(messages)
    await bot.change_presence(activity=discord. Activity(type=discord.ActivityType.watching, name=choice))


try: 
    # Run the bot with the provided Discord token
    bot.run(DISCORD_TOKEN)
except discord.HTTPException as e: 
    if e.status == 429: 
        logging.error("The Discord servers denied the connection for making too many requests") 
    else: 
        raise e
except Exception as e:
    import traceback
    logging.error(f"SOMETHING WENT WRONG STARTING THE BOT {e}")
    logging.error(''.join(traceback.TracebackException.from_exception(e).format()))

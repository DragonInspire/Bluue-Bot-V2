import typing
from discord.ext import commands, tasks
import discord
import logging
from discord import app_commands
from discord.ui import Select, View
from uniform import overlay_images
from online import get_online_players_with_data, FetchDataException, GuildDataException, fetch_data
from war import war_track, getWarData
from datetime import datetime
from pytz import timezone
from xp_tracking import contributions
from dotenv import load_dotenv
import os
from wynntils_parse import decode_item
import requests
import zaibatsu
from molah import invest, withdraw, getInvestments, emeraldTypesToEmeralds
import random
from mythicImage import mythicImage

devFlag = False

# Logging setup
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

# Load environment variables from a .env file
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

if (not devFlag):
    XP_LEADERBOARD_CHANNEL_ID = int(os.getenv('XP_LEADERBOARD_CHANNEL_ID'))
    ONLINE_PLAYER_CHANNEL = int(os.getenv('ONLINE_PLAYER_CHANNEL'))
    ONLINE_PLAYER_MESSAGE = int(os.getenv('ONLINE_PLAYER_MESSAGE'))


# Initialize the bot

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


# Define rank options
ranks = ["resident", "buke", "bushi", "shogun", "yako"]

zaibatsu_group = app_commands.Group(name="zaibatsu", description="mythic bank related commands")
bot.tree.add_command(zaibatsu_group)

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
        if not war_tracking.is_running() and not devFlag:
            war_tracking.start()
            logging.info("War tracking task started")
        else:
            logging.info("war tracking already started")
        '''
        if not war_update.is_running():
            war_update.start()
            logging.info("War update task started")
        else:
            logging.info("war update already started")
        '''
        if not xp_leaderboard.is_running() and not devFlag:
            xp_leaderboard.start()
            logging.info("xp leaderboard task started")
        else:
            logging.info("xp leaderboard already running")
    except Exception as e:
        logging.exception(f"unhandled exception while starting tasks {e}")
@zaibatsu_group.command(name="invest")
@app_commands.describe(player_name="player name: ")
@app_commands.describe(stack_invest="stack investment: ")
@app_commands.describe(liquid_invest="liquid investment")
@app_commands.describe(block_invest="block investment")
@app_commands.describe(emerald_invest="emerald investment: ")
async def zaibatsu_invest(interaction: discord.Interaction, player_name: str, stack_invest: typing.Optional[int]=0, liquid_invest: typing.Optional[int]=0, block_invest: typing.Optional[int]=0, emerald_invest: typing.Optional[int]=0):
    try:
        invest(player_name, [emerald_invest, block_invest, liquid_invest, stack_invest])
        await interaction.response.send_message(f"{player_name} investment of {[emerald_invest, block_invest, liquid_invest, stack_invest]} sucessful")
    except Exception as e:
        logging.info(e)
        await interaction.response.send_message(f"{player_name} investment of {[emerald_invest, block_invest, liquid_invest, stack_invest]} failed")
        
@zaibatsu_group.command(name="withdraw")
@app_commands.describe(player_name="player name: ")
@app_commands.describe(stack_withdraw="stack withdraw: ")
@app_commands.describe(liquid_withdraw="liquid withdraw")
@app_commands.describe(block_withdraw="block withdraw")
@app_commands.describe(emerald_withdraw="emerald withdraw: ")
async def zaibatsu_withdraw(interaction: discord.Interaction, player_name: str, stack_withdraw: typing.Optional[int]=0, liquid_withdraw: typing.Optional[int]=0, block_withdraw: typing.Optional[int]=0, emerald_withdraw: typing.Optional[int]=0):
    try:
        withdraw(player_name, [emerald_withdraw, block_withdraw, liquid_withdraw, stack_withdraw])
        await interaction.response.send_message(f"{player_name} withdraw of {[emerald_withdraw, block_withdraw, liquid_withdraw, stack_withdraw]} sucessful")
    except Exception as e:
        logging.info(e)
        await interaction.response.send_message(f"{player_name} withdraw of {[emerald_withdraw, block_withdraw, liquid_withdraw, stack_withdraw]} failed")    

@zaibatsu_group.command(name="investmentlist")
async def zaibatsu_investment_list(interaction: discord.Interaction):
    emerald_types = ["em", "eb", "le", "stx"]
    #try:
    investments = getInvestments()
    embed=discord.Embed(
        colour = discord.Colour.dark_teal(),
        title = "Mythic Bank Investments"
    )
    out = ""
    embed.set_thumbnail(url="https://static.wikia.nocookie.net/wynncraft_gamepedia_en/images/8/8c/Experience_bottle.png/revision/latest/scale-to-width-down/100?cb=20190118234414")
    for player in investments.keys():
        logging.debug(player)
        if not (investments[player][0] == 0 and investments[player][1] == 0 and investments[player][2] == 0 and investments[player][3] == 0):
            logging.debug(investments[player])
            for i in reversed(range(4)):
                logging.debug(investments[player][i])
                out += str(investments[player][i]) + " " + emerald_types[i] + " "

            out += "\n" + f"{emeraldTypesToEmeralds(investments[player]):,}" + " raw em"
            embed.add_field(name=player, value=out)
            out = ""
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
                          cost: typing.Optional[str] = "0", status: typing.Optional[str] = "in bank",
                           notes: typing.Optional[str] = "", wynntils: typing.Optional[str] = ""):
    out = zaibatsu.bought(player_name, mythic_name, overall=overall, cost=cost, status=status, notes=notes, wynntils=wynntils)
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
    out = zaibatsu.update(player_name, mythic_name, overall=overall, cost=cost, status=status, notes=notes, wynntils=wynntils)
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
    out = zaibatsu.rename(player_name, mythic_name, overall=overall, new_mythic_name=new_mythic_name, new_player_name=new_player_name, new_overall=new_overall)
    await interaction.response.send_message(out)

@zaibatsu_group.command(name="sell")
@app_commands.describe(mythic_name="mythicName:")
@app_commands.describe(player_name="playerName:")
@app_commands.describe(overall="item percent or other unique id")
@app_commands.describe(price="sell price")
async def zaibatsu_sell(interaction: discord.Interaction, mythic_name: str, player_name: str, overall: typing.Optional[str] = "", 
                          price: typing.Optional[str] = "0"):
    out = zaibatsu.sold(player_name, mythic_name, overall=overall, price=price)
    await interaction.response.send_message(out)

@zaibatsu_group.command(name="view")
@app_commands.describe(mythic_name="mythicName:")
@app_commands.describe(player_name="playerName:")
@app_commands.describe(overall="item percent or other unique id")
async def zaibatsu_view(interaction: discord.Interaction, mythic_name: str, player_name: str, overall: typing.Optional[str] = ""):
    out = zaibatsu.view(player_name, mythic_name, overall=overall)
    await interaction.response.send_message(out)

@zaibatsu_group.command(name="list")
@app_commands.describe(detailed="include data fields")
async def zaibatsu_list(interaction: discord.Interaction, detailed: typing.Optional[bool] = False):
    embed = discord.Embed(
        colour = discord.Colour.purple(),
        title = "Mythic Bank"
    )
    embed.set_thumbnail(url="https://www.wynndata.tk/assets/images/items/v4/unidentified/mythic.png")
    mythic_list = zaibatsu.list(detailed=detailed)
    for player in mythic_list.keys():
        embed.add_field(name=player, value=mythic_list[player], inline=False)
    embed.add_footer(text="be sure to include overall when using specific commands")
    await interaction.response.send_message(embed=embed)

@zaibatsu_group.command(name="display")
@app_commands.describe(mythic_name="mythicName:")
@app_commands.describe(player_name="playerName:")
@app_commands.describe(overall="item percent or other unique id")
@app_commands.describe(nori_command="check weigh pricecheck or any other nori command that takes wynntils string")
async def zaibatsu_display(interaction: discord.Interaction, mythic_name: str, player_name: str, overall: typing.Optional[str] = "", nori_command: typing.Optional[str] = "weigh"):
    try:
        wynntils = zaibatsu.getWynntils(player_name, mythic_name, overall=overall)
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
    embed.add_field(name="/uniform", value = "your minecraft skin with your farplane uniform!", inline=False)
    embed.add_field(name="/zaibatsu buy", value = "add a mythic to the mythic bank", inline=False)
    embed.add_field(name="/zaibatsu update", value="updates a mythic in the mythic bank", inline=False)
    embed.add_field(name="/zaibatsu rename", value="renames a mythic in the mythic bank", inline=False)
    embed.add_field(name="/zaibatsu sell", value="remove a mythic from the mythic bank", inline=False)
    embed.add_field(name="/zaibatsu view", value="view the data of a mythic in the mythic bank", inline=False)
    embed.add_field(name="/zaibatsu display", value="view the stats of a mythic if it has a saved wynntils string", inline=False)
    embed.add_field(name="/zaibatsu list", value="view all mythics in the bank", inline=False)
    embed.add_field(name="/zaibatsu invest", value="invest emeralds in the mythic bank", inline=False)
    embed.add_field(name="/zaibatsu withdraw", value ="withdraw emeralds from the mythic bank", inline=False)
    embed.add_field(name="/zaibatsu investmentlist", value="lists all emerald investments in the mythic bank", inline=False)
    
    
    await interaction.response.send_message(embed=embed)

# Command: Choose a uniform rank
@bot.tree.command(name="uniform")
@app_commands.describe(username="Username:")
async def uniform(interaction: discord.Interaction, username: str):
    try:
        logging.debug("Uniform command called")
        # Create a list of SelectOption for each rank
        optionList = list(map(lambda rankInList: discord.SelectOption(label=rankInList), ranks))
        
        # Create a Select component with the options
        select = Select(options=optionList)
        
        # Callback function for the selection
        async def my_callback(interaction):
            # Get the selected rank from the Select component
            choice = select.values[0]
            
            # Generate the uniform image and create a Discord file
            file = discord.File(overlay_images(username, choice), filename="uniform.png")
            logging.debug("Uniform file created")
            
            # Send a message with the uniform image
            await interaction.response.send_message(f"Hey {username}, here is your {choice} uniform", file=file)
            logging.debug("Uniform delivered")

        # Set the callback for the Select component
        select.callback = my_callback
        
        # Create a View with the Select component
        view = View()
        view.add_item(select)
        
        # Send a message with the Select component to choose a rank
        await interaction.response.send_message("Choose a rank", view=view)
        logging.debug("Choose rank message sent")
    except Exception as e:
        logging.exception(f"unhandled exception in uniform {e}")

# Background task: Fetch and display online players
@tasks.loop(seconds=30)
async def farplane_online():
    try:
        try:
            channel = bot.get_channel(ONLINE_PLAYER_CHANNEL)
            message = await channel.fetch_message(ONLINE_PLAYER_MESSAGE)
        except (discord.Forbidden, discord.NotFound) as e:
            logging.error(f"Error: Failed to get channel or message. {e}")
            return

        try:
            online_peoples = await get_online_players_with_data()
        except FetchDataException as e:
            logging.error(f"Error: Failed to get online players from Wynncraft API. {e}")
            await message.edit(content="Failed to fetch online players from Wynncraft")
            return
        except GuildDataException as e:
            logging.debug(f"No online players found {e}")
            embed = discord.Embed(
                colour = discord.Colour.blue(),
                title = "Online members of The Farplane guild"
            )
            embed.add_field(name = "no players online", value = "")
            embed.set_footer(text = "last updated " + datetime.now(timezone('EST')).strftime('%Y-%m-%d %H:%M:%S') + " EST")
            await message.edit(embed = embed)
            return

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

        embed.set_footer(text = "last updated " + datetime.now(timezone('EST')).strftime('%Y-%m-%d %H:%M:%S') + " EST")
        await message.edit(embed = embed)
    except Exception as e:
        logging.exception(f"unhandled exception in farplane online {e}")

# Background task: Track wars
@tasks.loop(minutes=10)
async def war_tracking():
    try:
        war_track()
    except Exception as e:
        logging.error(f"unhandled exception in war tracking {e}")
'''
# Background task: Update war data
@tasks.loop(minutes=10)
async def war_update():
    try:
        try:
            channel = bot.get_channel(1131996950548467782)  # Need to send a message to update
            message = await channel.fetch_message(1170050710948294687)
        except (discord.Forbidden, discord.NotFound) as e:
            logging.error(f"Error: Failed to get channel or message. {e}")
            return
        
        try:
            data = getWarData()
        except FileNotFoundError as e:
            # Handle the case where the file doesn't exist
            logging.error(f"File not found: {e}")
            await message.edit(content="Error: File not found")
            return
        except IOError as e:
            # Handle other input/output errors
            logging.error(f"IO Error: {e}")
            await message.edit(content="Error: Output error from file")
            return
        except Exception as e:
            # Handle other exceptions
            logging.error(f"An error occurred: {e}")
            await message.edit(content="Error: An unknown error occurred")
        else:
            # This block is executed if no exceptions occur
            logging.debug("File operations completed successfully")

        sorted_data = sorted(data, key=lambda x: x[1][0])
        if len(sorted_data) > 10:
            sorted_data = sorted_data[:10]
        
        printable_message = "**Farplane War Leaderboard**$```$"

        for player in sorted_data:
            printable_message += player
            printable_message += f" | successful wars {data[player][0]} | " 
            printable_message += f"total wars {data[player][1]}$"
        
        printable_message += f"```$Last update at {datetime.now()} UTC time"
        printable_message = printable_message.replace("$", "\n")
        await message.edit(content=printable_message)
    except Exception as e:
        logging.exception(f"unhandled exception in war update {e}")
'''
@tasks.loop(hours=24)
async def xp_leaderboard():
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
    messages = ["/uniform", "/zaibatsu"]
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

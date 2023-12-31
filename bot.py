from discord.ext import commands, tasks
import discord
import logging
from discord import app_commands
from discord.ui import Select, View
from uniform import overlay_images
from online import get_online_players_with_data, FetchDataException, GuildDataException
from war import war_track, getWarData
from datetime import datetime
from xp_tracking import contributions

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

DISCORD_TOKEN = ""

# Initialize the bot
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Define rank options
ranks = ["resident", "buke", "bushi", "shogun", "yako"]

# Event: Bot is ready
@bot.event
async def on_ready():
    logging.info("Bot is running")
    try:
        # Attempt to sync the commands with the server
        synced = await bot.tree.sync()
        logging.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logging.error(e)

    # Start background tasks
    try:
        if not farplane_online.is_running():
            farplane_online.start()
            logging.info("Farplane online task started")
        else:
            logging.info("farplane online already started")
        if not war_tracking.is_running():
            war_tracking.start()
            logging.info("War tracking task started")
        else:
            logging.info("war tracking already started")
        if not war_update.is_running():
            war_update.start()
            logging.info("War update task started")
        else:
            logging.info("war update already started")
        if not xp_leaderboard.is_running():
            xp_leaderboard.start()
            logging.info("xp leaderboard task started")
        else:
            logging.info("xp leaderboard already running")
    except Exception as e:
        logging.exception(f"unhandled exception while starting tasks {e}")

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
            channel = bot.get_channel(1131996950548467782)
            message = await channel.fetch_message(1131998219673538640)
        except (discord.Forbidden, discord.NotFound) as e:
            logging.error(f"Error: Failed to get channel or message. {e}")
            return

        try:
            online_peoples = get_online_players_with_data()
        except FetchDataException as e:
            logging.error(f"Error: Failed to get online players from Wynncraft API. {e}")
            await message.edit(content="Failed to fetch online players from Wynncraft")
            return
        except GuildDataException as e:
            logging.debug(f"No online players found {e}")
            printable_online = f"**Online members of The Farplane guild**$```$ No players online$```$Last update at {datetime.now()} UTC time"
            printable_online = printable_online.replace("$", "\n")
            await message.edit(content=printable_online)
            return

        printable_online = "**Online members of The Farplane guild**$```$"

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

        # Iterate through the dictionary and print the players in each world
        for world, players in world_players.items():
            printable_online += (f'World {world} $')
            for player_data in players:
                printable_online += (f'{player_data["rank"]}: {player_data["player"]} $')

        printable_online += f"```$Last update at {datetime.now()} UTC time"
        printable_online = printable_online.replace("$", "\n")
        await message.edit(content=printable_online)
    except Exception as e:
        logging.exception(f"unhandled exception in farplane online {e}")

# Background task: Track wars
@tasks.loop(minutes=10)
async def war_tracking():
    try:
        war_track()
    except Exception as e:
        logging.error(f"unhandled exception in war tracking {e}")

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

@tasks.loop(hours=24)
async def xp_leaderboard():
    try:
        daily_contributions = contributions()
        if len(daily_contributions) == 0:
            return
        daily_contributions = dict(sorted(daily_contributions.items(), key=lambda item: item[1]))
        list_10 = {}
        for i, key in enumerate(daily_contributions):
            if i > 9:
                break

            list_10[key] = daily_contributions[key]
        
        channel = bot.get_channel(1170580235998208072)

        printable_message = "**Farplane daily top 10 XP Contributions**$```$"
        for key in list_10:
            printable_message += f"{key} {list_10[key]}$"
        printable_message += f"```"
        printable_message = printable_message.replace("$", "\n")
        await channel.send(content=printable_message)
    except Exception as e:
        logging.exception(f"unhandled exception in xp leaderboard {e}")


try: 
    # Run the bot with the provided Discord token
    bot.run(DISCORD_TOKEN)
except discord.HTTPException as e: 
    if e.status == 429: 
        logging.error("The Discord servers denied the connection for making too many requests") 
    else: 
        raise e
except Exception as e:
    logging.error(f"SOMETHING WENT WRONG STARTING THE BOT {e}")
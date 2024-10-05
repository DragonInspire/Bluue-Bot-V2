# what can you do
# roll stickers once a week
# display your stickers
# have a profile to display your fav sticker + % of stickers collected

from random import choice
import json
from datetime import datetime, timedelta

sticker_map = {"fluid": "<:Fluid:1291807115492589650>",
                "fluid fanfare": "<:FluidFanfare:1291807128146677871>",
                "fluid fetus": "<:FluidFetus:1291807138665988156>",
                "fluid passive": "<:FluidPassive:1291807148510281729>",
                "fluid tryhard" :"<:FluidTryhard:1291807158911893595>",
                "kabocha": "<:Kabocha:1291807171692204043>",
                "kabocha attack": "<:KabochaAttack:1291807184241430569>",
                "kabocha drunk": "<:KabochaDrunk:1291807197034053632>",
                "kabocha hug": "<:KabochaHug:1291807210673803264>",
                "kabocha tpose": "<:KabochaTpose:1291807221759348807>",
                "kami": "<:Kami:1291807234917138442>",
                "kami bolt": "<:KamiBolt:1291807251647955005>",
                "kami glance": "<:KamiGlance:1291807264549769328>",
                "kami sip": "<:KamiSip:1291807278642495508>",
                "kami yeah": "<:KamiYeah:1291807294023274578>",
                "kumo": "<:Kumo:1291807324234715187>",
                "kumo bicep": "<:KumoBicep:1291807339636330496>",
                "kumo coin": "<:KumoCoin:1291807358246195241>",
                "kumo jump": "<:KumoJump:1291807375157891154>",
                "kumo stretch": "<:KumoStretch:1291807389808328745>",
                "kumo tune": "<:KumoTune:1291807403674963968>",
                "redd": "<:Redd:1291807419424309289>",
                "redd balloon": "<:ReddBalloon:1291807432607141959>",
                "redd coin": "<:ReddCoin:1291807447379607683>",
                "red graduate": "<:ReddGraduate:1291807464425128159>",
                "redd kumo": "<:ReddKumo:1291807480820662283>",
                "redd letter": "<:ReddLetter:1291807495479754905>",
                "redd my precious": "<:ReddMyPrecious:1291807512609423472>",
                "yang" : "<:Yang:1291812039249104958>",
                "yang caffeine": "<:YangCaffeine:1291807526689570817>",
                "yang coin": "<:YangCoin:1291807542401568890>",
                "yang hypno": "<:YangHypno:1291807558532599828>",
                "yang melt": "<:YangMelt:1291807575578251305>",
                "yang score": "<:YangScore:1291807596369547367>",
                "yin": "<:Yin:1291807610382848031>",
                "yin coin": "<:YinCoin:1291807621480710265>",
                "yin plane": "<:YinPlane:1291807637964591104>",
                "yin atlas": "<:Yintlas:1291807650065023078>",
                "yin toot": "<:YinToot:1291807662308069519>",
                "yin wave": "<:YinWave:1291807676199604347>"}

sticker_list = list(sticker_map.keys())
STICKERS_FILE = "./data/stickers.json"
PLAYER_FILE = "./data/rolls.json"

def loadData(DATA_FILE):
    data = None
    with open(DATA_FILE, "r") as file:
        data_str = file.read()
        data = json.loads(data_str)
    return data

def writeData(DATA_FILE, data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)

def time_until(target_date):
    current_date = datetime.now()
    time_difference = target_date - current_date
    return time_difference

def validate_roll(uuid):
    rolls = loadData(PLAYER_FILE)
    current_date = datetime.now()
    if uuid not in rolls:
        rolls[uuid] = str(current_date)
        writeData(PLAYER_FILE, rolls)
        return [True, None]
    
    stored_date = datetime.strptime(rolls[uuid], "%Y-%m-%d %H:%M:%S.%f")

    date_difference = current_date - stored_date

    if date_difference >= timedelta(days=7):
        rolls[uuid] = str(current_date)
        return [True, None]
    else:
        return [False, str(stored_date + timedelta(days=7))]

def roll_stickers(Embed, uuid):
    embed = Embed(
      colour = 3,
      title = "roll"
    )
    validation = validate_roll(uuid)
    if not validation[0]:
        wait_time = time_until(validation[1])
        days = wait_time.days
        seconds = wait_time.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        embed.add_field(name="sorry please wait before your next roll", value = f"{days}d {hours}h {minutes}m {seconds}s")
        return embed
    sticker = choice(sticker_list)

    player_sticker_lists = loadData(STICKERS_FILE)
    if uuid not in player_sticker_lists.keys():
        player_sticker_lists[uuid] = [sticker]
        writeData(STICKERS_FILE, player_sticker_lists)
        embed.add_field(name="congrats on your first sticker!", value=f"you rolled {sticker} {sticker_map[sticker]}!")
        return embed

    player_stickers = player_sticker_lists[uuid]

    if sticker in player_stickers:
        embed.add_field(name="unfortunately you got a dupe!", value="you rolled {sticker} {sticker_map[sticker]}!")
        return embed
    
    player_sticker_lists[uuid].append(sticker)
    writeData(STICKERS_FILE, player_sticker_lists)
    embed.add_field(name="you got a new sticker!", value=f"you rolled {sticker} {sticker_map[sticker]}!")
    return embed

def stickers_list(Embed):
    num_total_stickers = len(sticker_list)
    embed = Embed(
        colour = 3,
        title = f"sticker list! {num_total_stickers} stickers"
    )
    emojis = ""
    emojis_names = ""
    i = 1
    for sticker_name, sticker in sticker_map.items():
      emojis += sticker
      emojis_names += sticker_name + "\n"
      if i > 4:
        i = 0
        embed.add_field(name=emojis_names, value=emojis)
        emojis = ""
        emojis_names = ""
      
      i+=1

    return embed

def my_stickers(Embed, uuid):
    num_total_stickers = len(sticker_list)
    try:
      player_sticker_lists = loadData(STICKERS_FILE)
      player_stickers = player_sticker_lists[uuid]

      num_player_stickers = len(player_stickers)
      
      percent = round((num_player_stickers/num_total_stickers) * 100, 2)

      embed = Embed(
          colour = 3,
          title = f"you have these stickers! {num_player_stickers}/{num_total_stickers} {percent}%"
      )

      for sticker in player_stickers:
          embed.add_field(name=sticker, value=sticker_map[sticker])

      return embed
    except:
      embed = Embed(
          colour = 3,
          title = f"you have no stickers! 0/{num_total_stickers} 0%"
      )
      return embed

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
DATA_FILE = "./data/stickers.json"

def loadData():
    data = None
    with open(DATA_FILE, "r") as file:
        data_str = file.read()
        data = json.loads(data_str)
    return data

def writeData(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)

def time_until(target_date):
    current_date = datetime.now()
    time_difference = target_date - current_date
    return time_difference

def validate_roll(uuid):
    rolls = loadData()
    current_date = datetime.now()
    if uuid not in rolls:
        rolls[uuid] = current_date
        writeData(rolls)
        return [True, None]
    
    stored_date = rolls[uuid]

    date_difference = current_date - stored_date

    if date_difference >= timedelta(days=7):
        rolls[uuid] = current_date
        return [True, None]
    else:
        return [False, stored_date + timedelta(days=7)]

def roll_stickers(uuid):
    validation = validate_roll()
    if not validation[0]:
        wait_time = time_until(validation[1])
        days = wait_time.days
        seconds = wait_time.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"sorry please wait {days}d {hours}h {minutes}m {seconds}s"
    sticker = choice(sticker_list)

    player_sticker_lists = loadData()
    if uuid not in player_sticker_lists.keys():
        player_sticker_lists[uuid] = [sticker]
        writeData(player_sticker_lists)
        return f"congrats on your first sticker! you rolled {sticker} {sticker_map[sticker]}!"

    player_stickers = player_sticker_lists[uuid]

    if sticker in player_stickers:
        return f"unfortunately you got a dupe! you rolled {sticker} {sticker_map[sticker]}!"
    
    player_sticker_lists[uuid].append(sticker)
    writeData(player_sticker_lists)
    return "you got a new sticker! you rolled {sticker} {sticker_map[sticker]}!"

def stickers_list():
    num_total_stickers = len(sticker_list)
    message = f"{num_total_stickers} stickers \n"

    for name, sticker in sticker_map:
        message += f"{sticker} {name} \n"

    return message

def my_stickers(uuid):
    player_sticker_lists = loadData()
    player_stickers = player_sticker_lists[uuid]

    num_player_stickers = len(player_stickers)
    num_total_stickers = len(sticker_list)
    percent = round((num_player_stickers/num_total_stickers) * 100, 2)

    message = f"{num_player_stickers}/{num_total_stickers} {percent}% \n"

    for sticker in player_stickers:
        message += f"{sticker_map[sticker]} sticker \n"

    return message
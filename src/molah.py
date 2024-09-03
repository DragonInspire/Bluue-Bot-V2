import json
import logging
import math

DATA_FILE = "../data/molah.json"
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

def loadData():
    data = None
    try:
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
    except FileNotFoundError as e:
        # Handle the case where the file doesn't exist
        logging.error(f"File not found: {e}")
    except IOError as e:
        # Handle other input/output errors
        logging.error(f"IO Error: {e}")
    except Exception as e:
        # Handle other exceptions
        logging.error(f"An error occurred: {e}")
    else:
        # This block is executed if no exceptions occur
        logging.debug("File operations completed successfully")
        
    if data == None:
        logging.error("data is none type")
    return data

def writeData(data):
    try:
        with open(DATA_FILE, "w") as file:
            json.dump(data, file)
    except FileNotFoundError as e:
        # Handle the case where the file doesn't exist
        logging.error(f"File not found: {e}")
    except IOError as e:
        # Handle other input/output errors
        logging.error(f"IO Error: {e}")
    except Exception as e:
        # Handle other exceptions
        logging.error(f"An error occurred: {e}")
    else:
        # This block is executed if no exceptions occur
        logging.debug("File operations completed successfully")

def invest(player, amount, categories = ("initial", "raw")):
    data = loadData()
    amountLe = parsePrice(amount)
    if amountLe < 0:
        raise ValueError("negative money input")
    
    if player == "guild":
        for cat in categories:
            data["total"][cat] += amountLe
        writeData(data)
        return

    for cat in categories:
        player_money = 0
        
        if data is None:
            data = {}
        if "total" not in data:
            data["total"] = {"initial": 0, "raw": 0, "frozen": 0}
        if player not in data:
            data[player] = {"initial": 0, "raw": 0, "frozen": 0}
                
        player_money = data[player][cat]
        logging.debug(cat + " : " + toPriceStr(player_money))
        
        player_money += amountLe
        data[player][cat] = player_money
    
        data["total"][cat] += amountLe
    writeData(data)

def withdraw(player, amount, categories = ("initial", "raw")):
    data = loadData()
    amountLe = parsePrice(amount)
    if amountLe < 0:
        raise ValueError("negative money input")
    
    if player == "guild":
        for cat in categories:
            data["total"][cat] -= amountLe
            guildEnd = guildAmountNoLoad(data, cat)
            if guildEnd < 0 and cat != "initial":
                raise ValueError("negative money output")
        writeData(data)
        return

    for cat in categories:
        player_money = 0
        
        if data is None:
            data = {}
        if "total" not in data:
            data["total"] = {"initial": 0, "raw": 0, "frozen": 0}
        if player not in data:
            data[player] = {"initial": 0, "raw": 0, "frozen": 0}
                
        player_money = data[player][cat]
        logging.debug(cat + " : " + toPriceStr(player_money))
        
        player_money -= amountLe
        if player_money < 0 and cat != "initial":
            raise ValueError("negative money output")
        if player_money < 0 and cat == "initial": # if someone withdraws all their initial and some profit, don't go to negative initial
            player_money = 0
        data[player][cat] = player_money

        data["total"][cat] -= amountLe
    writeData(data)

def guildAmountNoLoad(data, cat):
    guild = data["total"][cat]
    for player in data.keys():
        if not (data[player][cat] == 0) and not player == "total":
            guild -= data[player][cat]
    return guild

def getInvestments(cat):
    data = loadData()
    out = {}
    for player in data.keys():
        logging.debug(player)
        if not (data[player][cat] == 0) and not player == "total":
            logging.debug(data[player][cat])
            out[player] = ""
            out[player] += toPriceStr(data[player][cat])
            out[player] += "\n" + f"{emeraldTypesToEmeralds(data[player][cat])}" + " em"


    guildAmount = guildAmountNoLoad(data, cat)
    logging.debug(guildAmount)
    if guildAmount != 0:
        out["guild"] = ""
        out["guild"] += toPriceStr(guildAmount)
        out["guild"] += "\n" + f"{emeraldTypesToEmeralds(guildAmount)}" + " em"

    totalAmount = data["total"][cat]
    logging.debug(totalAmount)
    out["total"] = ""
    out["total"] += toPriceStr(totalAmount)
    out["total"] += "\n" + f"{emeraldTypesToEmeralds(totalAmount)}" + " em"

    return out

def getProfit():
    data = loadData()
    out = {}
    categories = {"initial": -1, "raw":1, "frozen":1}
    
    for player in data.keys():
        logging.debug(player)
        player_profit = 0
        for cat, mult in categories.items():
            player_profit += data[player][cat] * mult
        if not player == "total":
            logging.debug(player_profit)
            out[player] = ""
            out[player] += toPriceStr(player_profit)
            out[player] += "\n" + f"{emeraldTypesToEmeralds(player_profit)}" + " em"

    guildAmount = 0
    for cat, mult in categories.items():
        guildAmount += guildAmountNoLoad(data, cat) * mult
    logging.debug(guildAmount)
    out["guild"] = ""
    out["guild"] += toPriceStr(guildAmount)
    out["guild"] += "\n" + f"{emeraldTypesToEmeralds(guildAmount)}" + " em"

    totalAmount = 0
    for cat, mult in categories.items():
        totalAmount += data["total"][cat] * mult
    logging.debug(totalAmount)
    out["total"] = ""
    out["total"] += toPriceStr(totalAmount)
    out["total"] += "\n" + f"{emeraldTypesToEmeralds(totalAmount)}" + " em"

    return out
            

def emeraldTypesToEmeralds(le):
    return le * 4096

def parsePrice(priceStr):
    priceStr = priceStr.lower()
    stxIdx = priceStr.find("stx")
    if stxIdx == -1:
        stx = 0
    else:
        stx = float(priceStr[:stxIdx])
        priceStr = priceStr[stxIdx + 3:]

    leIdx = priceStr.find("le")
    if leIdx == -1:
        le = 0
    else:
        le = float(priceStr[:leIdx])

    return int(le + stx * 64)
    
def toPriceArr(priceInt):
    n = ""
    if (priceInt < 0):
        n = "-"
        priceInt *= -1
    le = priceInt % 64
    stx = priceInt // 64
    return [le, stx]

def toPriceStr(priceInt):
    n = ""
    if (priceInt < 0):
        n = "-"
        priceInt *= -1
    le = priceInt % 64
    stx = priceInt // 64
    return f"{n}{stx} stx {n}{le} le"

def profit(priceInt, profitIntOrig):
    data = loadData()
    
    frozenTotalDivisor = data["total"]["frozen"] # get total for fracs before adding guild profit if positive
    guildFrozen = guildAmountNoLoad(data, "frozen")
    guildRaw = guildAmountNoLoad(data, "raw")
    # add profit to bank frozen total
    data["total"]["frozen"] += profitIntOrig
    profitInt = profitIntOrig
    
    # guild cut of profit or loss
    guild_cut = 0
    guild_cut_loss = 0
    guild_cut_raw_loss = 0
    if profitInt > 0: # profit
        guild_cut = 0.2
        profitInt *= 1.0 - guild_cut
    else: # loss
        guild_cut = 0.2
        guild_cut_loss = -1*profitInt * guild_cut
        if guild_cut_loss < guildFrozen:
            profitInt += guild_cut_loss
        else:
            logging.info(f"guild cant afford loss of {guild_cut_loss} from frozen {guildFrozen}")
            profitInt += guildFrozen
            frozenTotalDivisor -= guildFrozen # without reducing the guild frozen that was used to pay for loss it will go negative
            guild_cut_raw_loss = guild_cut_loss - guildFrozen
            logging.info(f"guild cant afford loss of {guild_cut_raw_loss} from raw {guildRaw}")
            if guild_cut_raw_loss > guildRaw:
                logging.info(f"guild cant afford loss of {guild_cut_raw_loss} from raw {guildRaw}")
                guild_cut_raw_loss = guildRaw
            guild_cut_raw_loss = int(math.floor(guild_cut_raw_loss))

    # logging.info(f"profitInt {profitInt}")

    # distribution of profit to player frozen
    # guild isn't a player, its implicit in the frozen fraction as whats left over after adding every other player
    for player in data:
        if player != "total":
            player_money_frozen = 1.0*data[player]["frozen"]
            player_frac = player_money_frozen / frozenTotalDivisor
            freeze = profitInt*player_frac
            player_money_frozen += freeze

            # logging.info(f"{player} frozen {player_money_frozen}")
            # logging.info(f"{player} freeze {freeze}")
            # logging.info(f"{player} player_frac {player_frac}")

            data[player]["frozen"] = int(math.floor(player_money_frozen))

    # distribution of sale price from frozen to raw
    # guild isn't a player, its implicit in the frozen fraction as whats left over after adding every other player
    frozenTotalDivisor = data["total"]["frozen"]
    for player in data:
        if player != "total":
            player_money_frozen = 1.0*data[player]["frozen"]
            player_money_raw = 1.0*data[player]["raw"]

            player_frac = player_money_frozen / frozenTotalDivisor
            unfreeze = priceInt*player_frac

            player_money_frozen -= unfreeze
            player_money_raw += unfreeze

            player_money_raw += guild_cut_raw_loss*player_frac # guild used raw to pay for cut of loss

            # logging.info(f"{player} frozen {player_money_frozen}")
            # logging.info(f"{player} raw {player_money_raw}")
            # logging.info(f"{player} freeze {unfreeze}")
            # logging.info(f"{player} player_frac {player_frac}")

            data[player]["frozen"] = int(math.floor(player_money_frozen))
            data[player]["raw"] = int(math.floor(player_money_raw))

    data["total"]["frozen"] -= priceInt
    data["total"]["raw"] += priceInt
    writeData(data)


def spend(priceInt):
    data = loadData()
    # distribution of buy price from raw to frozen
    # guild isn't a player, its implicit in the frozen fraction as whats left over after adding every other player
    rawTotal = data["total"]["raw"]
    for player in data:
        if player != "total":
            player_money_frozen = 1.0*data[player]["frozen"]
            player_money_raw = 1.0*data[player]["raw"]

            player_frac = player_money_raw / rawTotal
            freeze = priceInt*player_frac

            # logging.info(f"{player} frozen {player_money_frozen}")
            # logging.info(f"{player} raw {player_money_raw}")
            # logging.info(f"{player} freeze {freeze}")
            # logging.info(f"{player} player_frac {player_frac}")

            player_money_frozen += freeze
            player_money_raw -= freeze

            data[player]["frozen"] = int(math.floor(player_money_frozen))
            data[player]["raw"] = int(math.floor(player_money_raw))

    data["total"]["frozen"] += priceInt
    data["total"]["raw"] -= priceInt
    writeData(data)

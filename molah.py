import json
import logging

DATA_FILE = "molah.json"
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

def invest(player, amount):
    data = loadData()
    amountLe = parsePrice(amount)
    if amountLe < 0:
        raise ValueError("negative money input")
    
    if player == "guild":
        data["total"]["raw"] += amountLe
        writeData(data)
        return

    categories = ["initial", "raw"]
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
    
    data["total"]["raw"] += amountLe
    writeData(data)

def withdraw(player, amount):
    data = loadData()
    amountLe = parsePrice(amount)
    if amountLe < 0:
        raise ValueError("negative money input")
    
    if player == "guild":
        data["total"]["raw"] -= amountLe
        guildEnd = guildAmountNoLoad(data, "raw")
        if guildEnd < 0:
            raise ValueError("negative money output")
        writeData(data)
        return

    categories = ["initial", "raw"]
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
        if player_money < 0 and cat == "raw":
            raise ValueError("negative money output")
        if player_money < 0 and cat == "initial": # if someone withdraws all their initial and some profit, don't go to negative initial
            player_money = 0
        data[player][cat] = player_money
    
    data["total"]["raw"] -= amountLe
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

    if cat != "initial":
        guildAmount = guildAmountNoLoad(data, cat)
        logging.debug(guildAmount)
        out["guild"] = ""
        out["guild"] += toPriceStr(guildAmount)
        out["guild"] += "\n" + f"{emeraldTypesToEmeralds(guildAmount)}" + " em"

        totalAmount = data["total"][cat]
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
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

DATA_FILE = "zaibatsu.json"

def parsePrice(priceStr):
    priceStr = priceStr.lower()
    stxIdx = priceStr.find("stx")
    if stxIdx == -1:
        stx = 0
    else:
        stx = int(priceStr[:stxIdx])
        priceStr = priceStr[stxIdx + 3:]

    leIdx = priceStr.find("le")
    if leIdx == -1:
        le = 0
    else:
        le = int(priceStr[:leIdx])

    return le + stx * 64
    

def toPriceStr(priceInt):
    n = ""
    if (priceInt < 0):
        n = "-"
        priceInt *= -1
    le = priceInt % 64
    stx = priceInt // 64
    return f"{n}{stx} stx {n}{le} le"


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

def bought(playerName, mythicName, overall="", cost="", status="in bank", notes=None, date=datetime.today().strftime('%Y-%m-%d'), wynntils=""):
    data = loadData()

    if " ".join((playerName, mythicName, overall)) in data:
        return "this mythic is already in bank"
    data[" ".join((playerName, mythicName, overall))] = { "cost": cost, "status": status, "notes": notes, "date": date, "wynntils": wynntils }

    writeData(data)
    return "added"
     
def update(playerName, mythicName, overall="", cost=None, status=None, notes=None, date=None, wynntils=None):
    data = loadData()

    if " ".join((playerName, mythicName, overall)) not in data:
        return "this mythic is not in bank"
    
    # change data
    if cost is not None:
        data[" ".join((playerName, mythicName, overall))]["cost"] = cost
    if status is not None:
        data[" ".join((playerName, mythicName, overall))]["status"] = status
    if notes is not None:
        data[" ".join((playerName, mythicName, overall))]["notes"] = notes
    if date is not None:
        data[" ".join((playerName, mythicName, overall))]["date"] = cost
    if wynntils is not None:
        data[" ".join((playerName, mythicName, overall))]["wynntils"] = wynntils

    writeData(data)
    return "updated"

def rename(playerName, mythicName, overall="", new_mythic_name=None, new_player_name=None, new_overall=None):
    data = loadData()

    if " ".join((playerName, mythicName, overall)) not in data:
        return "this mythic is not in bank"
    
    # change id tuple
    if (new_mythic_name is not None) or (new_player_name is not None) or (new_overall is not None):
        item = data[" ".join((playerName, mythicName, overall))]
        
        if new_mythic_name is None:
            new_mythic_name = mythicName
        if new_player_name is None:
            new_player_name = playerName
        if new_overall is None:
            new_overall = overall

        if new_overall.lower() == "none":
            new_overall = ""
        
        del data[" ".join((playerName, mythicName, overall))]
        data[" ".join((new_player_name, new_mythic_name, new_overall))] = item

    writeData(data)
    return "renamed"

def sold(playerName, mythicName, overall="", price=""):
    data = loadData()

    if " ".join((playerName, mythicName, overall)) not in data:
        return "this mythic is not in bank"
    
    cost = data[" ".join((playerName, mythicName, overall))]["cost"]
    del data[" ".join((playerName, mythicName, overall))]

    costInt = parsePrice(cost)
    priceInt = parsePrice(price)
    profit = toPriceStr(priceInt - costInt)

    writeData(data)
    return "profit: " + profit

def view(playerName, mythicName, overall=""):
    data = loadData()

    if " ".join((playerName, mythicName, overall)) not in data:
        return "this mythic is not in bank"
    
    return json.dumps(" ".join((playerName, mythicName, overall))) + " : " + json.dumps(data[" ".join((playerName, mythicName, overall))])

def list(detailed=False):
    data = loadData()
    out = {}
    mythics = sorted(data.keys())

    for mythic_player in mythics:
        out[mythic_player] = ""
        if detailed:
            out[mythic_player] = data[mythic_player]
            del out[mythic_player]["wynntils"]
    
    return out

def getWynntils(playerName, mythicName, overall=""):
    data = loadData()
    wynntils = data[" ".join((playerName, mythicName, overall))].get("wynntils", "no wynntils string")
    return wynntils

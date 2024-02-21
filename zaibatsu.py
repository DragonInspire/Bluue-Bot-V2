import json
import logging
from datetime import datetime

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
    le = priceInt % 64
    stx = priceInt // 64
    return f"{stx} stx {le} le"


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

def bought(playerName, mythicName, overall=None, cost="", status="in bank", notes=None, date=datetime.today().strftime('%Y-%m-%d')):
    data = loadData()

    if " ".join((playerName, mythicName, overall)) in data:
        return "this mythic is already in bank"
    data[" ".join((playerName, mythicName, overall))] = { "cost": cost, "status": status, "notes": notes, "date": date }

    writeData(data)
    return "added"
     
def update(playerName, mythicName, overall=None, cost=None, status=None, notes=None, date=None):
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

    writeData(data)
    return "updated"

def rename(playerName, mythicName, overall=None, newMythicName=None, newPlayerName=None, newOverall=None):
    data = loadData()

    if " ".join((playerName, mythicName, overall)) not in data:
        return "this mythic is not in bank"
    
    # change id tuple
    if (newMythicName is not None) or (newPlayerName is not None) or (newOverall is not None):
        item = data[" ".join((playerName, mythicName, overall))]
        
        if newMythicName is None:
            newMythicName = mythicName
        if newPlayerName is None:
            newPlayerName = playerName
        if overall is None:
            newOverall = overall
        
        del data[" ".join((playerName, mythicName, overall))]
        data[" ".join((newPlayerName, newMythicName, newOverall))] = item

    writeData(data)
    return "renamed"

def sold(playerName, mythicName, overall=None, price=""):
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

def view(playerName, mythicName, overall=None):
    data = loadData()

    if " ".join((playerName, mythicName, overall)) not in data:
        return "this mythic is not in bank"
    
    return json.dumps(" ".join((playerName, mythicName, overall))) + " : " + json.dumps(data[" ".join((playerName, mythicName, overall))])

def list():
    data = loadData()
    out = ""
    mythics = sorted(data.keys())

    for mythic in mythics:
        out = out + mythic + "\n"
    
    return out
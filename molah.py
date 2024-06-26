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
    player_money = [0, 0, 0, 0]
    if data is None:
        data = {}
    for stored_player in data.keys():
        if stored_player == player:
            if data[player] != None:
                player_money = data[player]
        
    logging.debug(player_money)
    
    for i in range(4):
        player_money[i] += amount[i]
    player_money = autoConvert(player_money)
    data[player] = player_money
    
    writeData(data)

def withdraw(player, amount):
    data = loadData()
    player_money = [0, 0, 0, 0]
    if data is None:
        data = {}
    for stored_player in data.keys():
        if stored_player == player:
            if data[player] != None:
                player_money = data[player]
        
    logging.debug(player_money)
    
    for i in range(4):
        player_money[i] -= amount[i]
    player_money = autoConvert(player_money)
    data[player] = player_money
    
    writeData(data)

def autoConvert(money):
        if money[0] > 64:
            multiplier = money[0] // 64
            money[0] %= 64
            money[1] += 1 * multiplier
            return autoConvert(money)
        if money[1] > 64:
            multiplier = money[1] // 64
            money[1] %= 64
            money[2] += 1 * multiplier
            return autoConvert(money)
        if money[2] > 64:
            multiplier = money[2] // 64
            money[2] %= 64
            money[3] += 1 * multiplier
            return autoConvert(money)
        if money[0] < 0:
            multiplier = (-money[0] + 63) // 64  
            money[0] += 64 * multiplier
            money[1] -= multiplier
            return autoConvert(money)
        if money[1] < 0:
            multiplier = (-money[1] + 63) // 64  
            money[1] += 64 * multiplier
            money[2] -= multiplier
            return autoConvert(money)
        if money[2] < 0:
            multiplier = (-money[2] + 63) // 64  
            money[2] += 64 * multiplier
            money[3] -= multiplier
            return autoConvert(money)
        return money

def getInvestments():
    return loadData()

def emeraldTypesToEmeralds(ems):
    return (ems[3] * 262114) + (ems[2] * 4096) + (ems[1] * 64) + ems[0]

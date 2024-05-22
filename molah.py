import json
import logging

DATA_FILE = "molah.json"

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

def invest(player, amount):
    data = loadData()
    if data is None:
        data = {}
    if player in data:
        player_money = data[player]
        for i in range(3):
            player_money[i] += amount[i]
        data[player] = player_money
    writeData(data)

def withdraw(player, amount):
    data = loadData()
    if data is None:
        data = {}
    if player in data:
        player_money = data[player]
        for i in range(3):
            player_money[i] -= amount[i]
        data[player] = player_money
    writeData(data)

def autoConvert(player, data):
    for player_key in data.keys():
        if player_key == player:
            money = data[player_key]
            if money[0] > 64:
                money[0] -= 64
                money[1] += 1
                data[player_key] = money
                return autoConvert(player, data)
            if money[1] > 64:
                money[1] -= 64
                money[2] += 1
                data[player_key] = money
                return autoConvert(player, data)
            if money[0] < 0:
                money[0] += 64
                money[1] -= 1
                data[player_key] = money
                return autoConvert(player, data)
            if money[1] < 0:
                money[1] += 64
                money[2] -= 1
                data[player_key] = money
                return autoConvert(player, data)

def getInvestments():
    return loadData

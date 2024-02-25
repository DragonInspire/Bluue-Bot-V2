'''
Note - I am still trying to figure out how to calculate the actual values and percentages
onces this is done I will parse it into a discord sendable message
then I will add a file attatchment for the image of the mythic
'''

import requests
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

#decodes wynntils data
def decode_item(encoded_string) -> dict:
    # Current wynntils blocker format 
    # Update once artemis makes any changes
    START : str = "\U000F5FF0"
    END : str = "\U000F5FF1"
    SEPARATOR : str = "\U000F5FF2"
    RANGE_PATTERN : str = "[" + "\U000F5000" + "-" + "\U000F5F00" + "]"
    OFFSET : str = 0xF5000

    encoded_pattern : re.Pattern[str] = re.compile(
        START + "(?P<Name>.+?)" + SEPARATOR + "(?P<Ids>"
        + RANGE_PATTERN + "+)(?:" + SEPARATOR + "(?P<Powders>" + RANGE_PATTERN + "+))?(?P<Rerolls>" + RANGE_PATTERN + "+)" + END
    )

    def decode_numbers(text) -> list:
        return [ord(text[i]) - OFFSET for i in range(len(text))]

    match = encoded_pattern.match(encoded_string)
    if not match:
        return None

    name : str = match.group("Name")
    ids : list = decode_numbers(match.group("Ids"))
    powders : list = decode_numbers(match.group("Powders")) if match.group("Powders") else []
    rerolls : list= decode_numbers(match.group("Rerolls")) if match.group("Rerolls") else []

    return {
        "name": name,
        "identifications": ids,
        "powders": powders,
        "rerolls": rerolls
    }

def api_identifications(item_name) -> dict:
    wynncraft_api_url : str = f"https://api.wynncraft.com/v3/item/search/{item_name}"
    return requests.get(wynncraft_api_url).json()[item_name]["identifications"]


def get_item_percentages(wynntils_string) -> dict:
    # Stats matching and rate calculation
    decoded_item : dict = decode_item(wynntils_string)
    if not decoded_item:
        return None
    item_name : str = decoded_item["name"]
    identification_margins : dict = api_identifications(item_name)
    
    name = decoded_item['name']
    ids = decoded_item['identifications']

    # were going to do some shenanagins here because I dont know how to see the perminant stats so were just going to do list comprehension backwards
    ids.reverse()
    logging.info(f"the identification margins are {identification_margins}")
    reversed_identification_margins : dict= dict(reversed(list(identification_margins.items())))
    index : int = 0
    identification_percentages : list = []
    for identification in reversed_identification_margins:
        #logging.info(identification_margins[identification])
        if type(identification_margins[identification]) is int:
            break
        #logging.info(identification_margins[identification])
        id_min : int = identification_margins[identification]['min']
        id_max : int = identification_margins[identification]['max']
        id_value : int = ids[index]
        
        relative_value : int = id_value - id_min
        relative_max : int = id_max - id_min
        identification_percentage = round(relative_value / relative_max * 100, 2)
        logging.info(f"id min: {id_min}, id max: {id_max}, id value: {id_value}, identification percentage: {identification_percentage}")
        identification_percentages.append(identification_percentage)
        index += 1
    overall_percentage : float = round(sum(identification_percentages)/len(identification_percentages), 2)

    identification_percentages.reverse()
    ids.reverse()
    return {
        "name": name,
        "identifications": ids,
        "identification_percentages": identification_percentages,
        "overall_identification_percentages": overall_percentage
    }


#stat_order_url : str = "https://raw.githubusercontent.com/RawFish69/Nori/main/data/mythic_weights.json"
#stat_order : dict = fetch_stat_order()

'''encoded_messages = ["󵿰Fantasia󵿲󵁀󵀐󵀘󵁄󵀼󵁮󵁪󵿲󵂪󵀄󵿱", "󵿰Imperious󵿲󵀄󵀵󵁑󵀄󵀀󵿱", "󵿰Procrastination󵿲󵀘󵁅󵀨󵀀󵀈󵀔󵀀󵿱", "󵿰Cancer󵿲󵅉󵁼󵿲󵀫󵀀󵿱", "󵿰Libra󵿲󵀄󵀺󵀤󵀤󵀱󵀠󵿲󵀫󵀀󵿱", "󵿰Anxiolytic󵿲󵁢󵀶󵀈󵀈󵀈󵿲󵄃󵀀󵿱", "󵿰Capricorn󵿲󵀔󵀮󵀄󵀈󵿲󵀫󵀀󵿱"]
for message in encoded_messages:
    logging.info(decode_gear_item(message))'''

#logging.info(decode_item("󵿰Fantasia󵿲󵁀󵀐󵀘󵁄󵀼󵁮󵁪󵿲󵂪󵀄󵿱")["identifications"])
#logging.info(api_identifications("Fantasia"))


#logging.info(get_item_percentages("󵿰Fantasia󵿲󵁀󵀐󵀘󵁄󵀼󵁮󵁪󵿲󵂪󵀄󵿱"))

'''
-22 : 33.3%
-20 : 50.0%

+25 : 53.3%

-25 : 62.9%
-23 : 55.5%
-35 : 100%
-34 : 96.2%
'''

#[64, 16, 24, 68, 60, 110, 106]

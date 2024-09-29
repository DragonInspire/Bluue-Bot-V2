import requests
from io import BytesIO
from PIL import Image
import json
import base64
import logging

# Constants for skin URLs
SKIN_URLS = {
    "resident": "https://media.discordapp.net/attachments/1289229656666406924/1290004324415443065/mailmanresident.png?ex=66fae1a6&is=66f99026&hm=79dca9feb71ae620ab2455945693aae06a7a3aa27175cd31494ebf953c686680&=&format=webp&quality=lossless",
    "buke": "https://media.discordapp.net/attachments/1289229656666406924/1290004392434733191/mailmanbuke.png?ex=66fae1b6&is=66f99036&hm=d79a9f614dab9c6199ff149b7f8bde484e072eaeb48b6bef9d7ac4c282e72ca4&=&format=webp&quality=lossless",
    "bushi": "https://media.discordapp.net/attachments/1289229656666406924/1290004368531263539/mailmanbushi.png?ex=66fae1b0&is=66f99030&hm=a4fa4b5d962ad025bf78b74df547e9c0dc5212f8dcf103f34778336a3950b543&=&format=webp&quality=lossless",
    "shogun": "https://media.discordapp.net/attachments/1289229656666406924/1290004347484110982/mailmanshogun.png?ex=66fae1ab&is=66f9902b&hm=c9d8fdd5df87983ee44c5abab0af3ddca8921530ea14ee63bc6359e67d32b503&=&format=webp&quality=lossless",
    "yako": "https://media.discordapp.net/attachments/1289229656666406924/1290004513012453376/mailmanyako.png?ex=66fae1d3&is=66f99053&hm=cc8c948afeb06161740581121903468df2ec795233537bf135c14970de6068dd&=&format=webp&quality=lossless",
}

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

class MojangUUIDError(Exception):
    pass

class SkinImageError(Exception):
    pass

class OverlayImageError(Exception):
    pass

def get_mojang_uuid(username):
    try:
        response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
        response.raise_for_status()
        data = response.json()
        return data.get("id")
    except (requests.RequestException, ValueError) as e:
        raise MojangUUIDError(f"Error fetching Mojang UUID: {e}")

def get_skin_image(username):
    uuid = get_mojang_uuid(username)
    if uuid is None:
        return None

    try:
        response = requests.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}")
        response.raise_for_status()
        skin_data = response.json()
        properties = skin_data.get("properties", [])

        skin_url = next((prop["value"] for prop in properties if prop.get("name") == "textures"), None)
        if skin_url:
            skin_response = requests.get(json.loads(base64.b64decode(skin_url))["textures"]["SKIN"]["url"])
            skin_response.raise_for_status()
            return Image.open(BytesIO(skin_response.content))
        return None
    except (requests.RequestException, ValueError) as e:
        raise SkinImageError(f"Error fetching skin image: {e}")

def overlay_images(username, rank):
    background = get_skin_image(username)
    if background is None:
        raise OverlayImageError("Failed to get the user's skin image.")

    overlay_url = SKIN_URLS.get(rank)
    if overlay_url is None:
        raise OverlayImageError("Invalid rank.")

    try:
        overlay_response = requests.get(overlay_url)
        overlay_response.raise_for_status()
        overlay = Image.open(BytesIO(overlay_response.content))

        # Create a new image with RGBA mode and dimensions (64x64)
        new_img = Image.new("RGBA", (64, 64))

        # Paste the top-left quadrant (head) (32x16) of the user's skin onto the new image
        new_img.paste(background.crop((0, 0, 32, 16)))

        # Paste the bottom-left quadrant (hat) (32x5) of the user's skin onto the new image,
        # starting from coordinates (32, 11) on the new image
        new_img.paste(background.crop((32, 11, 64, 16)), (32, 11, 64, 16))

        # Create a new image with transparency (RGBA mode) to combine the background and overlay
        result = Image.new("RGBA", overlay.size)

        # Paste the background image onto the new image
        result.paste(new_img, (0, 0))

        # Paste the overlay image onto the new image with transparency using the overlay as a mask
        result.paste(overlay, (0, 0), mask=overlay)

        # Save the resulting image to a BytesIO stream in PNG format
        image_stream = BytesIO()
        result.save(image_stream, format="PNG")
        image_stream.seek(0)

        # Return the resulting image stream
        return image_stream
    except (requests.RequestException, ValueError) as e:
        raise OverlayImageError(f"Error fetching overlay image: {e}")

def save_image(image, filename):
    try:
        image.save(filename, format="PNG")
    except Exception as e:
        logging.error(f"Error saving image to file: {e}")

def get_head(username):
    skin = get_skin_image(username)
    base = skin.crop((8, 8, 16, 16))
    overlay = skin.crop((40,8,48,16))
    result = Image.new("RGBA", base.size)
    result.paste(base)
    result.paste(overlay, (0,0), overlay)

    result = result.resize((32, 32), Image.NEAREST)

    image_stream = BytesIO()
    result.save(image_stream, format="PNG")
    image_stream.seek(0)

    return image_stream

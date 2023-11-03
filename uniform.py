import requests
from io import BytesIO
from PIL import Image
import json
import base64

# Constants for skin URLs
SKIN_URLS = {
    "resident": "https://media.discordapp.net/attachments/566768030995054613/1131341745255358554/mailmanresident.png",
    "buke": "https://media.discordapp.net/attachments/566768030995054613/1131341745792225390/mailmanbuke.png",
    "bushi": "https://media.discordapp.net/attachments/566768030995054613/1131341746207465532/mailmanbushi.png",
    "shogun": "https://media.discordapp.net/attachments/566768030995054613/1131341746643664946/mailmanshogun.png",
    "yako": "https://media.discordapp.net/attachments/566768030995054613/1131341747134406717/mailmanyako.png",
}

def get_mojang_uuid(username):
    """
    Get the Mojang UUID for a given username.
    """
    try:
        response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
        response.raise_for_status()
        data = response.json()
        return data.get("id")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error fetching Mojang UUID: {e}")
    except (KeyError, TypeError):
        raise ValueError("Failed to retrieve the UUID for the given username.")

def get_skin_image(username):
    """
    Get the user's skin image.
    """
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
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error fetching skin image: {e}")
    except (KeyError, TypeError):
        raise ValueError("Failed to retrieve the skin image data.")

def overlay_images(username, rank):
    """
    Overlay the user's skin with the given rank.
    """
    skin = get_skin_image(username)
    if skin is None:
        raise ValueError("Failed to get the user's skin image.")

    overlay_url = SKIN_URLS.get(rank)
    if overlay_url is None:
        raise ValueError("Invalid rank.")

    try:
        overlay_response = requests.get(overlay_url)
        overlay_response.raise_for_status()
        overlay = Image.open(BytesIO(overlay_response.content))

        result = Image.alpha_composite(skin.convert("RGBA"), overlay.convert("RGBA"))
        return result
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error fetching overlay image: {e}")

def save_image(image, filename):
    """
    Save an image to a file.
    """
    image.save(filename, format="PNG")

# # Example usage
# try:
#     result_image = overlay_images("u89hsadwamifw", "resident")
#     save_image(result_image, "output_image.png")
# except ValueError as e:
#     print(f"Error: {e}")

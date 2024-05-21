from wynntilsresolver import GearItemResolver

def decode_item(encoded_item):
    decoded_item = GearItemResolver.from_utf16(encoded_item)
    return decoded_item

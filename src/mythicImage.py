mythic_adress = {"Convergence": "https://www.wynndata.tk/assets/images/items/v4//spear/spear--generic3.png",
                 "Quetzalcoatl": "https://www.wynndata.tk/assets/images/items/v4//wand/wand--air3.png",
                 "Epoch": "https://www.wynndata.tk/assets/images/items/v4//bow/bow--default2.png",
                 "Immolation": "https://www.wynndata.tk/assets/images/items/v4//relik/relik--fire3.png",
                "Oblivion": "https://www.wynndata.tk/assets/images/items/v4//dagger/dagger--generic3.gif",
                "Fatal": "https://www.wynndata.tk/assets/images/items/v4//wand/wand--thunder3.png",
                "Warp": "https://www.wynndata.tk/assets/images/items/v4//wand/wand--air3.png",
                "Singularity": "https://www.wynndata.tk/assets/images/items/v4//wand/wand--generic3.gif",
                "Revenant": "https://www.wynndata.tk/assets/images/items/v4//boots/boots--diamond.png",
                "Stratiformis": "https://www.wynndata.tk/assets/images/items/v4//bow/bow--air3.png",
                "Monster": "https://www.wynndata.tk/assets/images/items/v4//wand/wand--fire3.png",
                "Spring": "https://www.wynndata.tk/assets/images/items/v4//bow/bow--water3.png",
                "Absolution": "https://www.wynndata.tk/assets/images/items/v4//relik/relik--fire3.png",
                "Warchief": "https://www.wynndata.tk/assets/images/items/v4//boots/boots--diamond.png",
                "Gaia": "https://www.wynndata.tk/assets/images/items/v4//wand/wand--earth3.gif",
                "Collapse": "https://www.wynndata.tk/assets/images/items/v4//spear/spear--generic3.png",
                "Inferno": "https://www.wynndata.tk/assets/images/items/v4//dagger/dagger--fire3.png",
                "Nirvana": "https://www.wynndata.tk/assets/images/items/v4//dagger/dagger--water3.png",
                "Divzer": "https://www.wynndata.tk/assets/images/items/v4//bow/bow--thunder3.png",
                "Stardew": "https://www.wynndata.tk/assets/images/items/v4//boots/boots--diamond.png",
                "Fantasia": "https://www.wynndata.tk/assets/images/items/v4//relik/relik--generic3.gif",
                "Toxoplasmosis": "https://www.wynndata.tk/assets/images/items/v4//relik/relik--earth3.png",
                "Lament": "https://www.wynndata.tk/assets/images/items/v4//wand/wand--water3.png",
                "Thrundacrack": "https://www.wynndata.tk/assets/images/items/v4//spear/spear--thunder3.png",
                "Cataclysm": "https://www.wynndata.tk/assets/images/items/v4//dagger/dagger--thunder3.png",
                "Weathered": "https://www.wynndata.tk/assets/images/items/v4//dagger/dagger--air3.png",
                "Grimtrap": "https://www.wynndata.tk/assets/images/items/v4//dagger/dagger--earth3.png",
                "Dawnbreak": "https://www.wynndata.tk/assets/images/items/v4//boots/boots--diamond.png",
                "Nullification": "https://www.wynndata.tk/assets/images/items/v4//dagger/dagger--default2.png",
                "Sunstar": "https://www.wynndata.tk/assets/images/items/v4//relik/relik--thunder3.png",
                "Idol": "https://www.wynndata.tk/assets/images/items/v4//spear/spear--water3.png",
                "Ignis": "https://www.wynndata.tk/assets/images/items/v4//bow/bow--fire3.png",
                "Hadal": "https://www.wynndata.tk/assets/images/items/v4//relik/relik--water3.gif",
                "Grandmother": "https://www.wynndata.tk/assets/images/items/v4//bow/bow--earth2.png",
                "Moontower": "https://www.wynndata.tk/assets/images/items/v4//boots/boots--diamond.png",
                "Alkatraz": "https://www.wynndata.tk/assets/images/items/v4//spear/spear--earth1.png",
                "Guardian": "https://www.wynndata.tk/assets/images/items/v4//spear/spear--fire3.png",
                "Slayer": "https://www.wynndata.tk/assets/images/items/v4//boots/boots--diamond.png",
                "Olympic": "https://www.wynndata.tk/assets/images/items/v4//relik/relik--air3.png",
                "Freedom": "https://www.wynndata.tk/assets/images/items/v4//bow/bow--generic3.png",
                "Boreal": "https://www.wynndata.tk/assets/images/items/v4//boots/boots--diamond.png",
                "Galleon": "https://www.wynndata.tk/assets/images/items/v4//boots/boots--diamond.png",
                "Hero": "https://www.wynndata.tk/assets/images/items/v4//spear/spear--air3.png",
                "Resurgence": "https://www.wynndata.tk/assets/images/items/v4//boots/boots--diamond.png",
                "Discoverer": "https://www.wynndata.tk/assets/images/items/v4//chestplate/chestplate--diamond.png",
                "Crusade Sabatons": "https://www.wynndata.tk/assets/images/items/v4//boots/boots--diamond.png",
                "Aftershock": "https://www.wynndata.tk/assets/images/items/v4//relik/relik--earth3.png",
                "Az": "https://www.wynndata.tk/assets/images/items/v4//bow/bow--thunder3.png",
                "Apocalypse": "https://www.wynndata.tk/assets/images/items/v4//spear/spear--fire3.png",
                "Archangel": "https://www.wynndata.tk/assets/images/items/v4//spear/spear--air3.png",
                "Pure": "https://www.wynndata.tk/assets/images/items/v4//wand/wand--generic1.png",
                "Unknown": "https://www.wynndata.tk/assets/images/items/v4/unidentified/mythic.png"}

def mythicImage(mythic_name):
  try:
    adress = mythic_adress[mythic_name]
  except:
    adress = mythic_adress["Unknown"]
  return adress

def mythicList():
  my_list = []
  for mythic in mythic_adress.keys():
    my_list.append(mythic)
  my_list.pop()
  return my_list
  

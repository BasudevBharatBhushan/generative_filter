# Background
# Backgear - Back
# Hair - Back
# Sidekick
# Base Body
# Skin
# Clothes
# Head
# Hair - Front
# Mouth / Mouthwear
# Headwear
# Eyes
# Eyewear
# Ears
# Accessory**


import os
import glob
import random
from PIL import Image
  
import collections

layers_order = ["Background","Backgear","Hair","Sidekick","Base Body","Face","Skin","Mouth","Headwear","Eyes","Eyewear","Ears"]
BASE_ASSESTS_URL = "/Users/payas/work/degen/art"
all_layers = os.listdir(BASE_ASSESTS_URL)
all_layers.remove(".DS_Store")

assets = {}
for layer in all_layers:
    layer_path = os.path.join(BASE_ASSESTS_URL,layer)
    assets[layer] = []
    all_assests_in_layer = glob.glob(layer_path+"/*/*.png", recursive=True)
    for assest in all_assests_in_layer:
        assets[layer].append({
            "name":assest.split("/")[-1].split(".png")[0],
            "path":assest,
            "rarity":1,
            "layer":layer
            })


art_meta = []
picked_assests = []
for layer in layers_order:
    if assets[layer]:
        _picked_assest = random.choices(assets[layer],k=1)[0]
        picked_assests.append(_picked_assest)
       

art_meta.append(picked_assests)
picked_assests= []

print(len(art_meta))



for art in art_meta:
    print(art)
    bg = Image.open(art[0]["path"]) 
    background= bg.convert("RGBA")
    for layer in art:

        layer_image = Image.open(layer["path"])
        width = (background.width - layer_image.width) // 2
        height = (background.height - layer_image.height) // 2
        layer_image.show()
        background.paste(layer_image, (width, height), layer_image)
        background.save("new.png", format="png")
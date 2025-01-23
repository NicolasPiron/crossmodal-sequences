import os

first_img_cat = 'data/input/stims/characters/elsa_img.png'
first_img = os.path.basename(first_img_cat.split(".")[0].split("_")[0])

print(first_img)
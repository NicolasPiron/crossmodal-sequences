import os
import numpy as np
import random
from psychopy import visual, core, event
from sequences import stimuli_manager as sm

def check_slot_filling(start_item_img, images, slots, occ_count, win, background, out_path, txt):
    if occ_count == 5:
        resp = confirm_slot_filling(start_item_img, images, win, background, txt)
        if resp[0] == "space":
            running = save_slot_data(start_item_img, slots, out_path)
        elif resp[0] == "escape":
            reset_image_positions(images, slots)
            running = True
    else:
        running = True
    return running

def confirm_slot_filling(start_item_img, images, win, background, txt):
    validate = visual.TextStim(
        win,
        text=txt,
        pos=(0, 0),
        color="black",
    )
    background.draw()
    for img in images:
        if img["placed"]:
            img["stim"].draw()
    start_item_img.draw()
    validate.draw()
    win.flip()
    resp = event.waitKeys(keyList=["escape", "space"])
    return resp

def reset_image_positions(images, slots):
    for img in images:
        img["stim"].pos = img["orig_pos"]
        img["placed"] = False
    for slot in slots:
        slot["occupied"] = False
        slot["image"] = None
        slot["rect"].opacity = 1

def save_slot_data(start_item_img, slots, out_path):
    running = False
    first_img_path = start_item_img.image
    first_img_cat = sm.get_cat_from_stim(first_img_path)
    first_img = os.path.basename(first_img_path.split(".")[0].split("_")[0])
    with open(out_path, "w") as f:
        f.write("slot,stimulus,category\n")
        f.write(f"0,{first_img},{first_img_cat}\n")
        for i, slot in enumerate(slots):
            stim_path = slot["image"]["stim"].image
            stim_name = os.path.basename(
                            stim_path.split(".")[0].split("_")[0]
                        )
            stim_cat = sm.get_cat_from_stim(stim_path)
            f.write(f"{i+1},{stim_name},{stim_cat}\n")
    return running

def count_occupied_slots(slots):
    occ_count = 0
    for slot in slots:
        if slot["occupied"]:
            occ_count += 1
    return occ_count

def place_image_in_slot(slots, mouse, selected_image):
    for slot in slots:
        if mouse.isPressedIn(slot["rect"]) and not slot["occupied"]:
            # Move the selected image to the slot
            selected_image["stim"].pos = slot["rect"].pos
            selected_image["placed"] = True
            selected_image["highlight"].opacity = 0  # Remove highlight
            selected_image["current_slot"] = slot

            slot["occupied"] = True
            slot["image"] = selected_image
            slot["rect"].opacity = 0
            selected_image = None  # Reset selection
            core.wait(0.2)
            break

def toggle_image_selection(images, mouse, selected_image):
    for img in images:
        if mouse.isPressedIn(img["stim"]) and not img["placed"]:
            if selected_image == img:
                        # If the selected image is clicked again, unselect it
                selected_image["highlight"].opacity = 0
                selected_image = None
            else:
                        # Select a new image and highlight it
                if selected_image:
                    selected_image["highlight"].opacity = 0  # Remove highlight from previous selection
                selected_image = img
                img["highlight"].opacity = 1
            core.wait(0.2)  # Prevent rapid clicks
            break
    return selected_image

def undo_image_placement(images, mouse):
    for img in images:
        if mouse.isPressedIn(img["stim"]) and img["placed"]:
            # Undo the placement
            slot = img["current_slot"]
            img["stim"].pos = img["orig_pos"]  # Return to original position
            img["placed"] = False
            img["highlight"].opacity = 0
            img["current_slot"] = None

            if slot:
                slot["occupied"] = False
                slot["image"] = None
                slot["rect"].opacity = 1  # Make the slot visible again

            print(f"Removed {img['stim'].image} from slot.")
            core.wait(0.2)
            break


def gen_img_positions(jitter=0.1):
    ''' Generate a grid of image positions with some random jitter '''
    x = np.round(np.linspace(-0.75, 0.75, 6), 2)
    y = np.round(np.linspace(0.1, -0.85, 6), 2)
    positions = [(i, j) for i in x for j in y]
    y_jitter = jitter / 2

    positions = [(i + np.random.uniform(-jitter, jitter),
            j + np.random.uniform(-y_jitter, y_jitter))
        for i, j in positions]
    
    i_rm = random.randrange(len(positions))
    positions.pop(i_rm)

    return positions

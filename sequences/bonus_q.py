import os
import numpy as np
from psychopy import visual, event
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

def move_cursor(index: int, direction: str, total: int, cols: int, images) -> int:
    rows = int(np.ceil(total / cols))
    col = index // rows
    row = index % rows

    # Movement logic
    if direction == "up" and row > 0:
        row -= 1
    elif direction == "down" and row < rows - 1:
        row += 1
    elif direction == "left" and col > 0:
        col -= 1
    elif direction == "right" and col < cols - 1:
        col += 1
    else:
        return index  # no movement

    # Try to find next unplaced image in intended direction
    # We'll allow a limited number of attempts to avoid infinite loops
    max_attempts = rows * cols
    for _ in range(max_attempts):
        new_index = col * rows + row
        if new_index >= total:
            break
        if not images[new_index]["placed"]:
            return new_index

        # Move again in same direction
        if direction == "up" and row > 0:
            row -= 1
        elif direction == "down" and row < rows - 1:
            row += 1
        elif direction == "left" and col > 0:
            col -= 1
        elif direction == "right" and col < cols - 1:
            col += 1
        else:
            break

    # If no unplaced item found, return current index
    return index

def handle_select_or_place(images, index, selected_image, slots):
    img = images[index]
    if img["placed"]:
        return selected_image

    # Immediately try to place
    for slot in slots:
        if not slot["occupied"]:
            img["stim"].pos = slot["rect"].pos
            img["placed"] = True
            img["highlight"].opacity = 0
            img["current_slot"] = slot
            slot["occupied"] = True
            slot["image"] = img
            return None  # nothing is selected now

    return selected_image

def handle_undo(images):
    for img in images:
        if img["placed"]:
            slot = img["current_slot"]
            img["stim"].pos = img["orig_pos"]
            img["placed"] = False
            img["highlight"].opacity = 0
            img["current_slot"] = None
            slot["occupied"] = False
            slot["image"] = None
            slot["rect"].opacity = 1
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
    
    # removed this because need to put the dummy image
    # i_rm = random.randrange(len(positions))
    # positions.pop(i_rm)

    return positions

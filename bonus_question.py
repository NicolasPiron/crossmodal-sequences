from psychopy import visual, event, core
import random
import glob
import sequences.params as pm
import sequences.bonus_q as bq
import sequences.stimuli_manager as sm
from sequences.common import get_win_dict

def ask_sequence(start_item, seq_name, subject_id, run_id, win_dict):
    '''Ask the participant to place the images in the correct order and save the data'''

    out_path = f"{pm.output_dir}/sub-{subject_id}/sub-{subject_id}_run{run_id}_bonus_{seq_name}.csv"

    win = win_dict['win']
    background = win_dict['background']
    aspect_ratio = win_dict['aspect_ratio']

    instr2 = visual.TextStim(
        win, text="De quels items est composée cette séquence?", pos=(0, 0.7), color="black"
    )
    img_files = glob.glob(pm.input_dir + "/stims/*/*img.png")
    random.shuffle(img_files)
    start_item_path = glob.glob(pm.input_dir + f"/stims/*/{start_item}_img.png")[0]
    img_files.remove(start_item_path)
    positions = bq.gen_img_positions()

    start_item_img = visual.ImageStim(
        win,
        image=start_item_path,
        pos=(-0.75, 0.4),
        size=(pm.bq_img_size, pm.bq_img_size * aspect_ratio),
    )

    # define dictionaries for images and slots. This will allow us to keep track of what happens to them.
    images = []
    for i, img_path in enumerate(img_files):
        img_stim = visual.ImageStim(
            win,
            image=img_path,
            pos=positions[i],
            size=(pm.bq_img_size, pm.bq_img_size * aspect_ratio),
        )
        highlight = visual.Rect(
            win,
            width=pm.bq_hl_size,
            height=pm.bq_hl_size * aspect_ratio,
            pos=positions[i],
            lineColor="blue",
            lineWidth=5,
            opacity=0,
        )
        images.append(
            {
                "stim": img_stim,
                "highlight": highlight,
                "orig_pos": positions[i],
                "selected": False,
                "placed": False,
                "current_slot": None,
            }
        )

    slot_positions = [(-0.45, 0.4), (-0.15, 0.4), (0.15, 0.4), (0.45, 0.4), (0.75, 0.4)]
    slots = [
        {
            "rect": visual.Rect(
                win,
                width=pm.bq_img_size,
                height=pm.bq_img_size * aspect_ratio,
                pos=pos,
                lineColor="black",
                fillColor=(105, 105, 105),
            ),
            "occupied": False,
            "image": None,
        }
        for pos in slot_positions
    ]

    mouse = event.Mouse(win=win)
    selected_image = None  # Track the currently selected image
    running = True

    while running:
        background.draw()
        instr2.draw()
        start_item_img.draw()

        # Draw images and highlights
        for img in images:
            img["stim"].draw()
            img["highlight"].draw()
        for slot in slots:
            slot["rect"].draw()

        # Update the window
        win.flip()

        if mouse.getPressed()[0]:
            bq.undo_image_placement(images, mouse)
            selected_image = bq.toggle_image_selection(images, mouse, selected_image)
            bq.place_image_in_slot(slots, mouse, selected_image)

        occ_count = bq.count_occupied_slots(slots)
        running = bq.check_slot_filling(start_item_img, images, slots, occ_count, win, background, out_path)

        if "escape" in event.getKeys():
            running = False
    
    return win_dict

def ask_all_seq(subject_id, run_id, win_dict=None, set_seed=False):

    def shuffle_dict(d):
        items = list(d.items())
        random.shuffle(items)
        return dict(items)
    
    if win_dict is None:
        win_dict = get_win_dict()

    win = win_dict['win']
    background = win_dict['background']
    win.mouseVisible = True

   
    out_dir = f"{pm.output_dir}/sub-{subject_id}"
    try:
        sm.r_and_set_seed(out_dir)
    except FileNotFoundError as e:
        print(e)

    amodal_sequences = sm.generate_sequences(pm.input_dir, pm.seq_structures)
    amodal_sequences = shuffle_dict(amodal_sequences)

    background.draw()
    win.flip() 

    with open(pm.instr_bonus_fn, "r", encoding="utf-8") as file:
        txt = file.read()

    instructions = visual.TextStim(
        win, 
        text=txt, 
        pos=(0, 0), 
        color="black"
    )

    background.draw()
    instructions.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

    for seq in amodal_sequences:
        seq_name = seq[0]
        start_item = amodal_sequences[seq][0]
        ask_sequence(
            start_item, 
            seq_name=seq_name, 
            subject_id=subject_id,
            run_id=run_id,
            win_dict=win_dict
        )
        
    win.close()

if __name__ == "__main__":
    subject_id = '1001'
    run_id = '01'
    ask_all_seq(
        subject_id=subject_id, 
        run_id=run_id, 
        win_dict=None, 
        set_seed=True
    )
    core.quit()


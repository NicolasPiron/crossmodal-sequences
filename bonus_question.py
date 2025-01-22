from psychopy import visual, event, core
import random
import glob
import sequences.params as pm
import sequences.bonus_q as bq
import sequences.stimuli_manager as sm
import sequences.flow as fl
from sequences.common import get_win_obj

def ask_sequence(start_item, seq_name, subject_id, run_id, win=None):
    '''Ask the participant to place the images in the correct order and save the data'''

    out_path = f"{pm.output_dir}/sub-{subject_id}/sub-{subject_id}_run{run_id}_bonus_{seq_name}.csv"

    if win is None:
        win, background, aspect_ratio = get_win_obj(mouse_visible=True)
    else:
        _, background, _ = get_win_obj(mouse_visible=True)
        aspect_ratio = win.size[0] / win.size[1]

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
    
    return win

def ask_all_seq(subject_id, run_id, win=None):

    def shuffle_dict(d):
        items = list(d.items())
        random.shuffle(items)
        return dict(items)
    
    line1 = f"Run {run_id} terminé. Vous allez maintenant devoir reconstruire les séquences."
    line2 = "\nPour sélectionner un item, cliquez dessus. Pour le placer dans une case, cliquez sur la case."
    line3 = "\nUtilisez sur la touche ESPACE pour valider votre réponse, ou la touche ESC pour recommencer."
    line4 = "\n\nAppuyez sur ESPACE pour continuer."
    txt = line1 + line2 + line3 + line4

    if win is None:
        win, background, _ = get_win_obj()
    else:
        _, background, _ = get_win_obj()
    
    amodal_sequences = sm.generate_sequences(pm.input_dir, pm.seq_structures)
    amodal_sequences = shuffle_dict(amodal_sequences)

    background.draw()
    win.flip()
    fl.type_text(text=txt, win=win, background=background, t=pm.t)
    event.waitKeys(keyList=['space'])

    for seq in amodal_sequences:
        seq_name = seq[0]
        start_item = amodal_sequences[seq][0]
        win = ask_sequence(start_item, seq_name=seq_name, subject_id=subject_id, run_id=run_id, win=None)
    win.close()

if __name__ == "__main__":
    ask_all_seq(subject_id='01', run_id='01')
    core.quit()


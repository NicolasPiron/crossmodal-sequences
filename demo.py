import os
from psychopy.gui import DlgFromDict
from psychopy import visual, core, event
from sequences import flow as fl
import sequences.params as pm
from bonus_question import ask_all_seq


def run_demo():

    exp_info = {'ID': '00',
                'run': '01',
    }

    # run the experiment
    dlg = DlgFromDict(exp_info, title='Enter demo parameters', sortKeys=False)
    fl.handle_user_cancel(dlg)
    #fl.check_demo_info(exp_info)

    out_dir = "data/output/demo"
    os.makedirs(out_dir, exist_ok=True)
    if len(os.listdir(out_dir)) > 0:
        os.system(f"rm -r {out_dir}/*") # remove all files in the output directory

    # Create a window
    win = visual.Window(size=pm.win_size,
                        fullscr=True,
                        units='norm', 
                        screen=pm.screen,)
    win.mouseVisible = False
    aspect_ratio = win.size[0] / win.size[1]

    # Create the background image
    background = visual.ImageStim(
        win, 
        size=(2, 2*aspect_ratio),
        image=pm.bg_fn, 
        units="norm"
    )

    with open(pm.instr_fn, "r", encoding="utf-8") as file:
        instructions_text = file.read()

    instructions = visual.TextStim(
        win, text=instructions_text, font="Arial", color='black',  height=pm.text_height,
        alignText="center" )

    background.draw()
    instructions.draw()
    win.flip()
    fl.check_escape(win)
    event.waitKeys(keyList=['space'])

    return '01', 42, win

if __name__ == "__main__":
    subject_id, seed, win = run_demo()
    ask_all_seq(subject_id, seed, win)
    win.close()
    core.quit()

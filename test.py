import src.params as pm
from psychopy import visual, event, core
import src.stimuli_manager as sm
import glob
import byte_triggers as bt
import logging


out_dir = "data/output/sub-00"
    
logfn = f"{out_dir}/TEST_run-0_cmseq-logs-TEST.log"
pport = bt.MockTrigger()

bt.add_file_handler(logfn, mode='a', verbose='INFO')
logging.basicConfig(
        filename=logfn,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger()

win = visual.Window(
    size=pm.win_size,
    fullscr=True,
    units="norm",
    screen=pm.screen,
)
win.mouseVisible = False
aspect_ratio = win.size[0] / win.size[1]

background = visual.ImageStim(
    win, size=(2, 2 * aspect_ratio), image=pm.bg_fn, units="norm"
)

slot_positions = sm.get_slot_pos(y_pos=pm.y_pos)

slots = [
    {
        "rect": visual.Rect(
            win,
            width=pm.q_img_size,
            height=pm.q_img_size * aspect_ratio,
            pos=pos,
            lineColor="black",
            fillColor=(105, 105, 105)),
        "highlight": visual.Rect(
            win,
            width=pm.hl_size,
            height=pm.hl_size * aspect_ratio,
            pos=pos,
            lineColor="blue",
            lineWidth=5,
            opacity=0,
        ),
        "selected": False,
    }
    for pos in slot_positions
]

utils = {"win":win, "background":background, 'wait_fun':core.wait, 'event_fun':event.getKeys, 'trig_fun':pport.signal,
        'logger':logger, 'clear_event_fun':event.clearEvents}
 
start_item_paths = glob.glob(f"{pm.input_dir}/stims/animals/*_img.png")[:3]
end_item_paths = glob.glob(f"{pm.input_dir}/stims/animals/*_img.png")[-3:]

start_lst = [visual.ImageStim(
    win,
    image=start_item_path,
    pos=(-0.75, pm.y_pos),
    size=(pm.q_img_size, pm.q_img_size * aspect_ratio),
    )   for start_item_path in start_item_paths
]

end_lst = [visual.ImageStim(
    win,
    image=end_item_path,
    pos=(0, -pm.y_pos),
    size=(pm.q_img_size, pm.q_img_size * aspect_ratio),
    )   for end_item_path in end_item_paths
]

text_q_lst = ["Visualisez la sequence", "Placez l'item à la bonne position"]
instructions = [visual.TextStim(win=win,
        text=txt,
        pos=(0, 0.55),
        height=pm.text_height,
        color='black',
        units='norm'
    ) for txt in text_q_lst
]


for start_item, end_item in zip(start_lst, end_lst):
    resp_idx, rt = sm.run_question(utils, slots=slots, start_item=start_item, end_item=end_item,
                             instructions=instructions, triggers=[1, 3, 5], rt_clock=core.Clock(), global_clock=core.Clock())
    core.wait(0.01)
    print(f"Response index: {resp_idx}, RT: {rt}")
    idx2 = 3
    distance = sm.get_response_distance(resp_idx, idx2, rt)
    feedback_txt, font_color, correct = sm.get_feedback_args(distance)

    feedback = visual.TextStim(win=win,
        text=feedback_txt,
        pos=(0, 0),
        font='Arial',
        color=font_color, 
        height=pm.text_height,
        units='norm',
        bold=True
    )

    background.draw()
    feedback.draw()
    win.flip()
    core.wait(1)


#print(f"Chosen slot: {chosen_slot['rect'].pos}")

win.close()
core.quit()
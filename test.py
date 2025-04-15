# from pipeline import test_pipeline
# import faulthandler
# faulthandler.enable()

# if __name__ == "__main__":
#     for _ in range(100):
#         test_pipeline()

from psychopy import visual, core, event
import numpy as np
from sequences.common import get_win_dict


d = get_win_dict()
win = d["win"]
background = d["background"]
aspect_ratio = d["aspect_ratio"]

bar_c = '#254E70'
tick_c = '#254E70'
slider_c = 'white'
slider_lc = 'black'

y = -0.2
# linear spacing of the ticks between -0.4 and 0.4 with 7 ticks
far_l = -0.5
far_r = 0.5
slider_positions = np.linspace(far_l, far_r, 7)
bar_len = far_r - far_l
start_pos = 3  # start in the middle
# slider_positions = [-0.4, -0.3, -0.2, 0, 0.2, 0.3, 0.4]

txt = visual.TextStim(
    win,
    text="How focused were you during the block?",
    pos=(0, 0.5),
    color="black",
)

bar = visual.Rect(
    win,
    width=bar_len,
    height=0.05*aspect_ratio,
    fillColor=bar_c,
    pos=(0, y),
)
slider = visual.Rect(
    win,
    width=0.02,
    height=0.1*aspect_ratio,
    fillColor=slider_c,
    lineColor=slider_lc,
    pos=(slider_positions[start_pos], y),
)

ticks = [
    visual.Rect(
        win,
        width=0.01,
        height=0.05*aspect_ratio,
        fillColor=tick_c,
        pos=(x, y),
    )
    for x in slider_positions
]

def move_slider(slider, current_pos, keys):
    if 'left' in keys:
        current_pos -= 1 if current_pos > 0 else 0
    elif 'right' in keys:
        current_pos += 1 if current_pos < len(slider_positions) - 1 else 0
    pos = slider_positions[current_pos]
    slider.pos = (pos, y)
    return current_pos

background.draw()
txt.draw()
bar.draw()
slider.draw()
win.flip()

current_pos = start_pos
run = True
while run:
    keys = event.getKeys()
    if 'space' in keys:
        run = False
        print(f'User selected the value : {current_pos+1}')
    current_pos = move_slider(slider, current_pos, keys)
    background.draw()
    txt.draw()
    bar.draw()
    for tick in ticks:
        tick.draw()
    slider.draw()
    win.flip()
    core.wait(0.01)


core.wait(1)
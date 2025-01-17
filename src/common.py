from psychopy import visual
import src.params as pm

def get_win_obj(mouse_visible=False):
    win = visual.Window(
        size=pm.win_size,
        fullscr=True,
        units="norm",
        screen=pm.screen,
    )
    aspect_ratio = win.size[0] / win.size[1]
    background = visual.ImageStim(
        win,
        size=(2, 2 * aspect_ratio), 
        image=pm.bg_fn, units="norm"
    )
    win.mouseVisible = mouse_visible
    return win, background, aspect_ratio
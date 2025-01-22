from psychopy import visual
import sequences.params as pm

def get_win_obj(mouse_visible=False):
    '''Create a window object and a background object'''
    win = visual.Window(
        size=pm.win_size,
        fullscr=True,
        units="norm",
        color=pm.bg_color,
        screen=pm.screen,
    )
    aspect_ratio = win.size[0] / win.size[1]
    background = visual.ImageStim(
        win,
        size=(2, 2 * aspect_ratio),
        image=pm.bg_fn,
        units="norm"
    )
    win.mouseVisible = mouse_visible
    return win, background, aspect_ratio
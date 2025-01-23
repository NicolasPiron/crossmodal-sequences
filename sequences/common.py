from psychopy import visual
import sequences.params as pm

def get_win_dict(mouse_visible=False):
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
    d = {"win": win, "background": background, "aspect_ratio": aspect_ratio}
    return d
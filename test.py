from psychopy import visual, core
from stimuli.audio import Sound
from sequences.common import get_win_dict
import time
import matplotlib.pyplot as plt


win_d = get_win_dict()
win = win_d["win"]
bg = win_d["background"]
vis_stim = visual.ImageStim(
    win=win,
    image='data/input/stims/en/bodyparts/arm_img.png',
    size=(0.5, 0.5 * win_d["aspect_ratio"]),
    units="norm",
    pos=(0, 0),
)
snd = Sound('data/input/sounds/seq_sounds/bass.wav')

def wait_frate(win, objects:list, frate:int, t:int):
    ''' Function to wait for a certain number of frames '''
    # Calculate the number of frames to wait
    frames = int(frate * t)
    # Wait for the specified number of frames
    for _ in range(frames):
        for obj in objects:
            obj.draw()
        win.flip()

times = []
clock = core.Clock()
for _ in range(100):
    bg.draw()
    vis_stim.draw()
    snd.play()
    win.flip()
    clock.reset()
    wait_frate(win, [bg, vis_stim], 120, 1)
    t = clock.getTime()
    print(t)
    times.append(t)
    
win.close()

fig, ax = plt.subplots()
ax.hist(times, bins=20)
ax.set_xlabel('Time (s)')
ax.set_ylabel('Frequency')
ax.set_title('Histogram of Times')
plt.show()


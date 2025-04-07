# from pipeline import test_pipeline
# import faulthandler
# faulthandler.enable()

# if __name__ == "__main__":
#     for _ in range(100):
#         test_pipeline()

import numpy as np

def move_cursor(index:int, direction:str, total:int, cols:int, images):
    rows = int(np.ceil(total / cols))
    row = index // cols
    col = index % cols

    if direction == "left" and row > 0:
        row -= 1
    elif direction == "right" and row < rows - 1:
        row += 1
    elif direction == "up" and col > 0:
        col -= 1
    elif direction == "down" and col < cols - 1:
        col += 1

    new_index = row * cols + col
    # Skip placed images
    # while new_index < total and images[new_index]["placed"]:
    #     new_index = (new_index + 1) % total
    return new_index

i = move_cursor(5, "right", 30, 6, [])
print(i)
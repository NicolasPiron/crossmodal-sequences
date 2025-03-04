# from pipeline import test_pipeline
# import faulthandler
# faulthandler.enable()

# if __name__ == "__main__":
#     for _ in range(100):
#         test_pipeline()


import os
import glob
lang = 'fr'
all_items = glob.glob(f"data/input/stims/{lang}/*/*.png")
all_items = sorted(set([os.path.basename(item).split('_')[0] for item in all_items]))   
for item in all_items:
    print(item)
    print('---')
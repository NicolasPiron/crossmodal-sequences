from pathlib import Path
import os
from sequences.params import input_dir, instr_fnames

def get_txt(lang:str, instr_fn:str)-> str:
    ''' Load instruction text from file '''
    lang = lang if lang in os.listdir(f"{input_dir}/instructions") else 'fr' # default to french
    fn = instr_fnames[instr_fn]
    fn = Path(f"{input_dir}/instructions/{lang}/{fn}")
    txt = read_instr(fn)
    return txt

def read_instr(fn:str)-> str:
    ''' Read instruction text from file '''
    with open(fn, 'r') as fn:
        txt = fn.read()
    return txt

def get_path(lang:str)-> Path:
    ''' Get path to instruction text '''
    return Path(f"{input_dir}/instructions/{lang}")

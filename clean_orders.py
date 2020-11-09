import glob
import os
import sys
import json 

def clean():
    files = glob.glob(os.path.join(sys.path[0], "data/*.txt"))
    for file in files:
        with open(file, 'r') as f:
            blob = json.load(f)
            

clean()
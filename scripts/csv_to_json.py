#!/usr/bin/python3

# Rebuilds the JSON database from the CSV files

import pandas
import os
import glob

def files_in_folder(folder):
    """Returns a list of files in the folder and all
    its subfolders recursively. The folder can be
    written with wildcards as with the Unix find command.
    """
    files = []
    for f in glob.glob(folder):
        if os.path.isdir(f):
            files.extend(files_in_folder(f + os.sep + "**"))
        else:
            files.append(f)
    return files

print(files_in_folder("csv/i7/bernoulli_logit_lpmf"))
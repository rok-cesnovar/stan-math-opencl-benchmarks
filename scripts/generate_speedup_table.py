#!/usr/bin/python3

import os
import json
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

def print_speedup_info(data, function_name, args, base_device, speedup_device):
    for data_param in data:
        sizes_base = data[data_param][base_device]["mean"][0]
        times_base = data[data_param][base_device]["mean"][1]
        sizes_speedup = data[data_param][speedup_device]["mean"][0]
        times_speedup = data[data_param][speedup_device]["mean"][1]
        sizes = []
        speedup = []
        max_speedup = 0
        first_n_faster = 0
        for i in range(len(sizes_base)):
            speedup = times_base[i]/times_speedup[i]
            if sizes_base[i] == sizes_speedup[i]:
                if speedup > max_speedup:
                    max_speedup = speedup
                if speedup > 1.3 and first_n_faster == 0:
                    first_n_faster = sizes_base[i]
        print(function_name, args, data_param, first_n_faster, "%2.2f" % max_speedup, sep = ";")

base_device = "i7"
speedup_device = "radeonvii"

for f_name in files_in_folder("json"):
    function_name = f_name.split("/")[1].split(".")[0]
    with open(f_name) as f:
        data = json.load(f)
    for args in data:
        print_speedup_info(data[args], function_name, args, base_device, speedup_device)
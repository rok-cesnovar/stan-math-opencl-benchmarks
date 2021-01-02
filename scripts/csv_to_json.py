#!/usr/bin/python3

# Builds JSON files from CSV files
#
# The CSV files need to be placed in a device subfolder.
# Devices subfolder are labeled with a shorthand that is described in detail in the device.json file.
# The device folder

import os
import glob
import csv
import json

csv_data = {}


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


def parse_sig(sig):
    function_args = sig.split("/")[0]
    size = int(sig.split("/")[1])
    time_type = sig.split("/")[2]
    first_prim = function_args.find("Prim")
    first_rev = function_args.find("Rev")
    if first_rev == -1:
        args_start = first_prim
    elif first_prim == -1:
        args_start = first_rev
    else:
        args_start = min(first_prim, first_rev)
    function = function_args[: args_start - 1]
    args = function_args[args_start:].split("_")
    data_params = ""
    types = ""
    for i in range(len(args)):
        if i % 2 == 0:
            if args[i] == "Prim":
                data_params += "data,"
            else:
                data_params += "param,"
        else:
            new_type = args[i]
            if new_type == "int1":
                new_type = "array[] int"
            types += new_type + ","
    return function, types[:-1], data_params[:-1], size, time_type


def process_file(csv_filename):
    line_off = 0
    device_label = csv_filename.split("/")[1]
    with open(csv_filename) as f:
        # google benchmark writes some non-csv data at beginning
        for line in iter(f.readline, ""):
            if line.startswith("name,iterations"):
                f.seek(f.tell() - len(line) - line_off, os.SEEK_SET)
                break
            line_off = -1
        data = csv.reader(f)
        header_read = False
        for i in data:
            if not header_read:
                header_read = True
                continue
            function, types, data_params, s, t = parse_sig(i[0])
            if not (function in csv_data):
                csv_data[function] = {}
            function_data = csv_data[function]
            if not (types in function_data):
                function_data[types] = {}
            sig_types_data = function_data[types]
            if not (data_params in sig_types_data):
                sig_types_data[data_params] = {}
            sig_data = sig_types_data[data_params]
            if not (device_label in sig_data):
                sig_data[device_label] = {"mean": [[], []], "stddev": [[], []]}
            sig_device_data = sig_data[device_label]
            if t == "manual_time_mean":
                sig_device_data["mean"][0].append(s)
                sig_device_data["mean"][1].append(float(i[2]))
            if t == "manual_time_stddev":
                sig_device_data["stddev"][0].append(s)
                sig_device_data["stddev"][1].append(float(i[2]))


for f in files_in_folder("csv"):
    process_file(f)

for f in csv_data:
    with open("json/" + f + ".json", "w") as fp:
        json.dump(csv_data[f], fp, indent=4, sort_keys=True)

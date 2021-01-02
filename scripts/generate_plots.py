#!/usr/bin/python3

import os
import json
import glob

def pick_color(n):
    str_bit_reversed_n = "{:015b}".format(n + 1)[::-1]
    r = 0.9 * ((int(str_bit_reversed_n[0::3], 2) / 2.0 ** 5 + 0.3) % 1)
    g = 0.9 * ((int(str_bit_reversed_n[1::3], 2) / 2.0 ** 5 + 0.3) % 1)
    b = 0.9 * ((int(str_bit_reversed_n[2::3], 2) / 2.0 ** 5 + 0.3) % 1)
    return r, g, b

def plot_speedup(data, function_name, args, base_device, speedup_device, plot_log_y=False):
    import matplotlib
    import matplotlib.pyplot as plt
    
    matplotlib.use("Agg")
    
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.set_tight_layout(True)
    ax.set_xscale("log")
    if plot_log_y:
        ax.set_yscale("log")
    ax.set_xlabel("size")
    ax.set_ylabel("speedup")
    
    color_n = 1
    for data_param in data:
        sizes_base = data[data_param][base_device]["mean"][0]
        times_base = data[data_param][base_device]["mean"][1]
        sizes_speedup = data[data_param][speedup_device]["mean"][0]
        times_speedup = data[data_param][speedup_device]["mean"][1]
        sizes = []
        speedup = []
        for i in range(len(sizes_base)):
            if sizes_base[i] == sizes_speedup[i]:
                sizes.append(sizes_base[i])
                speedup.append(times_base[i]/times_speedup[i])
        ax.plot(
            sizes,
            speedup,
            "x",
            color=pick_color(color_n),
            label="_nolegend_",
        )
        ax.plot(
            sizes,
            speedup,
            label=data_param,
            color=pick_color(color_n),
        )
        color_n = color_n + 1

    [
        spine.set_visible(False)
        for loc, spine in ax.spines.items()
        if loc in ["top", "right", "left", "bottom"]
    ]
    ax.minorticks_off()
    ax.grid()
    ax.legend()
    ax.set_title(function_name + "(" + args + ")")
    fig_dir = "figs/"+speedup_device+"_vs_"+base_device
    if not os.path.isdir(fig_dir):
        os.mkdir(fig_dir)
    if plot_log_y:
        suffix = "__log_y"
    else:
        suffix = ""
    fig_name = fig_dir + "/" + function_name + "__" + args.replace(",", "-").replace(" ", "_")+suffix
    if not os.path.isfile(fig_name):
        fig.savefig(fig_name, bbox_inches="tight", dpi=300)
    plt.close()

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

base_device = "i7"
speedup_device = "radeonvii"

for f_name in files_in_folder("json"):
    function_name = f_name.split("/")[1].split(".")[0]
    print(function_name)
    with open(f_name) as f:
        data = json.load(f)
    for args in data:
        plot_speedup(data[args], function_name, args, base_device, speedup_device)
        plot_speedup(data[args], function_name, args, base_device, speedup_device, plot_log_y = True)
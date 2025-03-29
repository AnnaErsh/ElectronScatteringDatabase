"""
This module downloads all the datafiles from the Quasielastic Electron Nucleus Scattering Archive
"""

import requests
import os
import time

folders = [
    "E12-14-012_totUncertainties",
    "E12-14-012_statUncertainties",
    "E08-014",
    "E02-019",
    "Miho_12C",
    "2H",
    "3H",
    "3He",
    "4He",
    "6Li",
    "12C",
    "16O",
    "27Al",
    "40Ca",
    "48Ca",
    "56Fe",
    "197Au",
    "208Pb",
    "238U",
    "Other",
    "nms",
    "nmt",
]
webpage = "http://discovery.phys.virginia.edu/research/groups/qes-archive/data/"
output_folder = "scrapped_data"

for folder in folders:
    datatype = ".dat" if folder != "E08-014" else ".zip"
    try:
        dat_response = requests.get(webpage + folder + datatype, timeout=10)
        if dat_response.status_code == 200:
            filename = f"{folder + datatype}"
            filepath = os.path.join(output_folder, filename)
            with open(filepath, "wb") as f:
                if datatype == ".dat":
                    f.write(dat_response.content)
                    print(f"Downloaded: {filename}")
                else:
                    for chunk in dat_response.iter_content(chunk_size=1024):
                        f.write(chunk)
                        print(f"Downloaded contents of {filepath} to {folder}")
        else:
            print(f"Failed to download {webpage + folder + datatype}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {webpage + folder}: {e}")

    time.sleep(2)

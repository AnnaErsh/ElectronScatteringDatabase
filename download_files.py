"""
This module downloads all the datafiles from the Quasielastic Electron Nucleus Scattering Archive
"""

import os
import time
import requests

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
WEBPAGE = "http://discovery.phys.virginia.edu/research/groups/qes-archive/data/"
OUTPUT_FOLDER = "scrapped_data"

for folder in folders:
    file_extension = ".dat" if folder != "E08-014" else ".zip"
    try:
        dat_response = requests.get(WEBPAGE + folder + file_extension, timeout=10)
        if dat_response.status_code == 200:
            filename = f"{folder + file_extension}"
            filepath = os.path.join(OUTPUT_FOLDER, filename)
            with open(filepath, "wb") as f:
                if file_extension == ".dat":
                    f.write(dat_response.content)
                    print(f"Downloaded: {filename}")
                else:
                    for chunk in dat_response.iter_content(chunk_size=1024):
                        f.write(chunk)
                        print(f"Downloaded contents of {filepath} to {folder}")
        else:
            print(f"Failed to download {WEBPAGE + folder + file_extension}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {WEBPAGE + folder}: {e}")

    time.sleep(2)

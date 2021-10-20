import logging
import os
import json
import re
import sys
from time import strftime, localtime

t = localtime()
time_string = strftime("%m-%d-%Y", t)
# --- data ---
# profiles = ['kbz-security-sso', 'sap-prod-sso', 'kbz-crayon-sso', 'kbz-temenos-i-sso', 'kbz-kbzt-sso']
profiles = ['kbz-kbzt-sso']

# --- file write formart ---
file_name = "route_id"
sfile_name = "new_route_tableIds"
efile_name = "route_tables_info"
output = "json"
fformat = "txt"

##########################
recordRouteId = []


class LOG:
    log_filepath = "../log/"
    os.makedirs(log_filepath, exist_ok=True)

    logger = logging.getLogger("aws")
    # handlar
    hr_stream = logging.StreamHandler()
    hr_file = logging.FileHandler(log_filepath + "route_migrate_{}.log".format(time_string))
    infohr_file = logging.FileHandler(log_filepath + "route_info_{}.log".format(time_string))

    # Level
    hr_stream.setLevel(logging.INFO)
    hr_file.setLevel(logging.ERROR)
    infohr_file.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter("%(levelname)s %(asctime)s  %(message)s")
    hr_stream.setFormatter(formatter)
    hr_file.setFormatter(formatter)
    infohr_file.setFormatter(formatter)

    # add handler
    logger.addHandler(hr_stream)
    logger.addHandler(hr_file)
    logger.addHandler(infohr_file)
    logger.setLevel(logging.DEBUG)


def file_write_handler(fine_name, fdata, rformat, arg):
    try:
        with open(f'../{fine_name}.{rformat}', arg) as output:
            json.dump(fdata, output)
        LOG.logger.info(f"File Record is done {file_name}.{rformat}")
    except Exception as e:
        LOG.logger.error(f"{e}")


def file_read_handler(file_name, rformat):
    if os.stat(f'../{file_name}.{rformat}').st_size == 0:
        LOG.logger.warning("File data is empty")
    else:
        with  open(f'../{file_name}.{rformat}') as f:
            if re.search("txt$", rformat):
                test = f.read()
            elif re.search("json$", rformat):
                test = json.load(f)
        return test


# Simple app don't used
def writeTempFile(text=None):
    filePath = "/temp/file1.txt"
    if not text:  # If not provided return file content
        f = open(filePath, "r")
        slug = f.read()
        return slug
    else:
        f = open(filePath, "a")  # Create a blank file
        f.seek(0)  # sets  point at the beginning of the file
        f.truncate()  # Clear previous content
        f.write(text)  # Write file
        f.close()  # Close file
        return text

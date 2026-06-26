import os
import logging
import json

log = logging.getLogger(__name__)

PROGRAM_DIR = os.path.dirname(os.path.abspath(__file__))

def get_config(name:str) -> dict:
    '''Attempts to grab a .conf file by root name, and falls back to .example.conf suffix if it fails.'''
    fsuffix = ".conf"
    for i in range(2): # lol
        fname = f"{name}{fsuffix}"
        fpath = os.path.join(PROGRAM_DIR, fname)
        log.debug(f"Trying to access '{fpath}'")
        if os.path.exists(fpath):
            try: 
                with open(fpath, "r") as f:
                    config = json.load(f)
                    f.close()
                log.info(f"Config '{name}' load was successful.")
                return config
            except json.JSONDecodeError:
                log.error(f"Failed to decode '{fname}', malformed JSON.")
            except:
                log.error(f"Unhandled exception while trying to decode '{fname}'", exc_info=True)
        else:
            logmsg = f"Target file path '{fpath}' does not exist."
            if fsuffix == ".conf": log.warning(f"{logmsg} Example config will be used.") # this is okay, we can fallback to the stock example.conf
            if fsuffix == ".example.conf": log.error(f"{logmsg} Pull the examples from the GitHub repository.")
        fsuffix = ".example.conf" # try again, but using the examples as a fallback (this condition happens if .conf suffix fails)
    log.error(f"No configuration was loaded for '{name}', Spark may not operate correctly (or not at all)!")
    return {} # blank dict
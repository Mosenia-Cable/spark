import os, json
import logging
import datetime as DT
import requests
import xmlproc as XML

PROGRAM_DIR = os.path.dirname(os.path.abspath(__file__))

log = logging.getLogger('spark')

def get_config(name:str):
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

def fetch_guide(endpoint_type:str,endpoint_url:str,date:DT.datetime) -> None|str:
    '''Fetches XMLTV (as a string) for the appropriate endpoint and the date provided.'''
    guide = None
    if endpoint_type == "4broadcast":
        # collect API response from 4broadcast
        request_date = date.strftime("%m/%d")
        request_url = f"{endpoint_url}/guide/{request_date}?xmltv=true"
        r = requests.get(request_url)
        r.raise_for_status()
        guide = r.content.decode() # assumes that we received a proper bytestring of XML response
    
    return guide

def parse_and_collect(channels:dict, date:DT.datetime=DT.datetime.now()) -> list:
    '''Parses the channel definitions (channels) and runs the fetch tasks for each and for the specified date. Returns a list of pipe-separated program lines, in the OnCable format.'''
    records = []
    for channel in channels:
        # process the channel number into the OnCable-friendly numbers
        channel_number = channel.get("num", None)
        subchannel = None
        try:
            v = str(float(channel_number)).split(".") # HEHEHE LOL THIS IS DIABOLICAL (but, it works...)
            channel_number = v[0].rjust(3, "0") # (in HU-961 voice) "FIRST DIGIT."
            subchannel = v[1][:1] # (in HU-961 voice) "SECOND DIGIT." - only one digit on the minor channel
            if subchannel == "0": subchannel = None # null it out if there's no subchannel
        except:
            log.warning(f"Invalid value for 'num' in channel definition: {channel}, this definition will be ignored")
            continue # skip this bad definition
        # collect the channel's callsign

        channel_info = {
            "ch_num": channel_number,
            "subch": subchannel,
        }
        # prepare collection for the proper endpoint types
        endpoint_url = channel.get("endpoint", None)
        endpoint_type = channel.get("type", "4broadcast") # assume 4broadcast if unspecified
        endpoint_target = channel.get("target_id", None) # if unspecified, we'll just grab the first channel in XMLTV
        guide_xml = fetch_guide(endpoint_type, endpoint_url, date)
        if guide_xml:
            XML.XMLTV2DEL(guide_xml, endpoint_target, channel_info)
            # to-do, process these to a file



if __name__ == "__main__":
    import coloredlogs
    coloredlogs.install("DEBUG")
    channels = get_config('channels')
    parse_and_collect(channels)
    
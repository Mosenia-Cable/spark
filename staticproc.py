"Processes statically-configured channels with a single, continuous program."
import datetime as DT
import logging

log = logging.getLogger(__name__)
    

def DICT2DEL(channel_info:dict, program_info:dict, date:DT.datetime):
    # channel info
    ch_num = channel_info.get("ch_num", "000") # e.g. 004
    ch_letters = str(program_info.get("ch_letters", f"CH{ch_num}")) # e.g. "VBA4", "WVVN", or "Undefi"
    subch = channel_info.get("subch", None) # e.g. "4"
    if not subch: subch = ""
    # time info
    start_time = "00:00" # start at midnight
    date = date.strftime("%m/%d/%Y") # e.g. 06/25/2026
    dur_minutes = "1440" # 24-hour static program
    # title info
    p_titles = program_info.get("titles", ["Undefined Program", "Undefined"])
    title = p_titles[0] # first title, the longest raw title
    title_long = p_titles[1 % len(p_titles)] if p_titles[1 % len(p_titles)] != title else "" # if it equals raw title, ignore
    title_medium = p_titles[2 % len(p_titles)] if p_titles[2 % len(p_titles)] != title else "" # if it equals raw title, ignore
    title_short = p_titles[3 % len(p_titles)] if p_titles[3 % len(p_titles)] != title else "" # if it equals raw title, ignore 
    title_shortest = p_titles[4 % len(p_titles)] if p_titles[4 % len(p_titles)] != title else "" # if it equals raw title, ignore
    # episode and programming details
    episode = str(program_info.get("episode", "")) # e.g. "Joe Runs To The Mall"
    year = str(program_info.get("year", "")) # e.g. 2026
    program_type = str(program_info.get("program_type", "0")) # e.g. "0" for Default
    desc = str(program_info.get("desc", "")) # e.g. "This is a description of a standard fixed program which does absolutely nothing other than represent a channel."
    category = str(program_info.get("category", "")) # e.g. "Drama"
    actor = str(program_info.get("actor", "")) # e.g. "Joe Zap2It"
    country = str(program_info.get("country", "")) # e.g. "USA" or "USA/CAN"
    tmsid = str(program_info.get("tmsid", "")) # e.g. "EP0481938501395391" idk and don't care but maybe some other people do so here you go
    # ratings
    star_rating = str(program_info.get("stars", "")) # e.g. "*****" - me in GTA btw
    rating_A = str(program_info.get("rating", "")) # e.g. "TVPG"
    rating_desc = str(program_info.get("advisories", "")) # e.g. "Mild violence"
    rating_B = rating_A # dupe
    # qualifiers
    is_HD = "Y" if program_info.get("hd", False) == True else "N" # HD identifier
    qualifiers_A = ""
    qualifiers_A += "CC" if program_info.get("captions", False) == True else "" # captions present
    qualifiers_A += "ST" if program_info.get("stereo", False) == True else "" # stereo sound present
    qualifiers_A += "BW" if program_info.get("color", True) == False else "" # black and white
    qualifiers_B = ""
    unk_A = ""
    unk_B = ""
    unk_C = ""
    unk_D = ""
    
    DEL = "|".join([
        ch_num, # channel number
        date, start_time, # time variables
        ch_letters, # callsign
        dur_minutes, # program length
        title, title_long, title_medium, title_short, title_shortest, # titles
        episode, # episode name
        unk_A,
        star_rating, # rating
        year, # release year
        program_type, # program type number
        category, # genre/category in text
        actor, # name of an individual actor
        rating_A, rating_desc, # MPAA/TVPG rating + advisories
        qualifiers_A, qualifiers_B, # special qualifiers
        desc, # program description
        unk_B,
        rating_B, # unsure
        unk_C,
        country, # country of origin
        tmsid, # gracenote program ID
        unk_D,
        is_HD, # Y/N indicator of HD or SD
        subch # subchannel number 
    ])
    DEL = DEL.replace("\n","") # no new lines!
    DEL = DEL.encode("ascii",errors="ignore") # encode into ASCII to eliminate yucky Unicode
    DEL = DEL.decode("ascii") # decode bytes back to ASCII text
    log.debug(f"Successfully built static program '{title}' for channel '{ch_letters}'.")

    return DEL # return our delimited string
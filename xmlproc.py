'''Processes the XMLTV data into OnCable delimited string lines.'''
import logging
log = logging.getLogger(__name__)
import xml.etree.ElementTree as ET
import datetime as DT

def conv_program(program:ET.Element, channel_info:dict):
    '''Converts a <programme> to a delimited-formatted entry (pipe-separated data)'''
    # make <video> tag available
    p_video = program.find("video")
    # make <audio> tag available
    p_audio = program.find("audio")
    # station-related objects
    ch_num = channel_info.get("ch_num") # e.g. 004
    ch_letters = channel_info.get("ch_letters") # e.g. "VBA4", "WVVN", or "Undefi"
    subch = channel_info.get("subch", None) # e.g. "4"
    if not subch: subch = ""
    # time-related objects
    p_start_time = program.attrib.get("start") # e.g. 20260623000000 -0500
    p_stop_time = program.attrib.get("stop") # e.g. 20260623000000 -0500
    p_release = program.find("date") # e.g. 20040218
    if p_release: p_release = p_release.text # date code is in the text of this tag
    DT_START = DT.datetime.strptime(p_start_time, "%Y%m%d%H%M%S %z").astimezone(tz=DT.timezone.utc) # zap2it processes program data in UTC.
    DT_STOP = DT.datetime.strptime(p_stop_time, "%Y%m%d%H%M%S %z").astimezone(tz=DT.timezone.utc) # UGHHHH has to be UTC. i hate UTC
    DT_RELEASE = None
    if p_release: DT_RELEASE = DT.datetime.strptime(p_release, "%Y%m%d") # convert to datetime if we found one
    year = ""
    if DT_RELEASE: year = f"{DT_RELEASE.year}"
    date = DT_START.strftime("%m/%d/%Y") # e.g. 06/25/2026
    start_time = DT_START.strftime("%H:%M") # e.g. 11:00
    dur_minutes = str((DT_STOP - DT_START).total_seconds() / 60) # get minutes by math
    # program titles
    p_titles = [t.text for t in program.findall("title")] # get each title text as strings
    p_titles = sorted(p_titles, reverse=True, key=len) # sort from longest to shortest
    if len(p_titles) == 0: p_titles = ["Unknown Program"] # fallback in case the XMLTV response was faulty
    title = p_titles[0] # first title, the longest raw title
    title_long = p_titles[1 % len(p_titles)] if p_titles[1 % len(p_titles)] != title else "" # if it equals raw title, ignore
    title_medium = p_titles[2 % len(p_titles)] if p_titles[2 % len(p_titles)] != title else "" # if it equals raw title, ignore
    title_short = p_titles[3 % len(p_titles)] if p_titles[3 % len(p_titles)] != title else "" # if it equals raw title, ignore 
    title_shortest = p_titles[4 % len(p_titles)] if p_titles[4 % len(p_titles)] != title else "" # if it equals raw title, ignore
    # program episode info
    episode = "" # episode title, e.g. "Soft Lock"
    p_sub_title = program.findall("sub-title")
    for st in p_sub_title: # at some point i will make a preferred language target
        episode = st.text # for now, though, just collect the first instance
        break
    # star rating info
    p_star_ratings = program.findall("star-rating")
    star_rating = "" # e.g. "***"
    for r in p_star_ratings:
        if r.attrib.get("system") == "TV Guide": # target TV Guide ratings, it delivers the 5-star format that Zap2It anticipates
            stars = {"0/5":"", "1/5":"*", "2/5":"**", "3/5":"***", "4/5":"****", "5/5":"*****"} # convert numerical rating to asterisks
            r_r = r.find("value") # because star-rating tags contain more information, such as the <icon> tag, the actual rating is stored in <value>
            if r_r: star_rating = stars.get(r_r.text) # get the converted asterisk string
            break # we found our star rating, carry on
    # maturity rating info
    p_maturity_ratings = program.findall("rating")
    rating_A = "" # e.g. "TV-14", "PG-13"
    for r in p_maturity_ratings:
        if r.attrib.get("system") == "MPAA": # (Movies) target Motion Pictures Association rating, Zap2It anticipates this (?)
            r_r = r.find("value") # because rating tags contain more information, such as the <icon> tag, the actual rating is stored in <value>
            rating_A = r_r.text
            break # found rating, carry on
        elif r.attrib.get("system") == "TVPG": # (TV series) target TV Parental Guide rating, Zap2It anticipates this (?)
            r_r = r.find("value") # because rating tags contain more information, such as the <icon> tag, the actual rating is stored in <value>
            rating_A = r_r.text
            break # found rating, carry on
    rating_B = rating_A # we're not sure why this exists, in existing data it is a duplicate of A
    rating_desc = "" # the rating advisories are not currently part of the XMLTV scope, there's really not a good way to collect this. maybe 4broadcast will introduce a custom tag?
    # program type + category/genre objects
    PROGRAM_TYPES = { # maybe move this to a .conf file for ease of customization?
        # definitions match OnCable program type codes
        "series": "0", "music": "0", "drama": "0", "sitcom": "0", # Default
        "movie":"1", "movies": "1", "film": "1", # Movie
        "sports": "5", # Sports
        "news": "25", # News
        "kids": "12", "cartoons": "17", "cartoon": "17" # Kids
    }
    p_genres = program.findall("category")
    category = "Unknown"
    program_type = "0" # default to normal program if we no category was specified
    for c in p_genres:
        category = c.text.capitalize() # overwriting category will at least give us something, even if not matched to program type
        program_type = PROGRAM_TYPES.get(category.lower(), "0") # look up the category in the dict
        if program_type: break # grab the first match as the absolute definition
        # to-do: create a priority system, because a "Cartoon" category may also be a "Series" category
    # actor object
    p_credits = program.find("credits") # according to XMLTV DTD, there is only one 'credits' tag
    actor = "" # e.g. "Jerry Seinfeld"
    if p_credits: 
        p_actor = p_credits.find("actor") # OnCable delimited only displays ONE actor
        if p_actor: actor = p_actor.text # get single actor
    # qualifiers objects
    qualifiers_A = "" # e.g. "CCSTBW" where CC indicates closed captions, ST stereo sound, BW black & white
    p_subtitles = program.findall("subtitles")
    for s in p_subtitles: # closed captions qualifier
        s_type = s.attrib.get("type", None)
        if s_type:
            if s_type == "teletext": # only target teletext as the condition for CC. 
                # my reasoning for this is that CC is an embedded OPTIONAL broadcast feature; NOT a definition of fixed, permanently imposed on-screen captions.
                qualifiers_A += "CC"
                break # exit this loop
    if p_audio: # stereo sound qualifier
        STEREO_QUALITIES = ["stereo", "dolby digital", "dolby", "bilingual", "surround"] # forced to lowercase for consistency
        p_stereo = p_audio.findall("stereo")
        for s in p_stereo:
            if s.text.lower() in STEREO_QUALITIES: # lookup lowercase for consistency
                qualifiers_A += "ST"
                break # exit this loop
    if p_video: # black & white qualifier
        p_colour = p_video.find("colour")
        if p_colour:
            if p_colour.text == "no": qualifiers_A += "BW"

    qualifiers_B = "" # e.g. "Live". TBD on how to collect this information

    # country object
    country = "" # e.g. "United States" or "USA/GBR" or "USA/CAN", or "Canada"
    COUNTRIES = {
        "US": ["United States", "USA"], # evidence in data
        "CA": ["Canada", "CAN"], # evidence in data
        "AU": ["Australia", "AUS"], # assumed
        "DE": ["Germany", "DEU"], # assumed
        "RU": ["Russia", "RUS"], # assumed
        "GB": ["GBR", "GBR"] # lol, okay? that's just how it is in the sample data from 6/21/2021
    }
    p_countries = program.findall("country") # 'country' tags in XMLTV are either full country name or two-letter country code
    if len(p_countries) == 1: country = COUNTRIES.get(p_countries[0].text, [p_countries[0].text])[0] # only one country so get the text and translate to full name, fallback to original text if fail
    if len(p_countries) > 1: # if more than one country in definition
        for c in p_countries: 
            n = COUNTRIES.get(c.text, [None, None])[1] # get two-letter country code
            if n: 
                if len(country) == 0: country += n # add it without any special chars
                else: country += f"/{n}" # prefix with a /
    # tmsid (Gracenote program ID) object
    tmsid = ""
    p_tmsid = program.findall("episode-num")
    for i in p_tmsid:
        if i.attrib.get("system") == "dd_progid":
            tmsid = i.text.replace(".","") # in the zap2it data, the TMSID exists but does NOT have a decimal point for the last 4 digits
    # is it HD? object
    is_HD = "N" # default to no
    HD_VALUES = ["HDTV", "HD", "4K", "4KTV", "1920X1080", "2560X1080", "1440X1080"] # just abiding by XMLTV, i guess? forced to uppercase for consistency
    if p_video:
        p_quality = p_video.find("quality")
        if p_quality: 
            if p_quality.text.upper() in HD_VALUES: is_HD = "Y" # if the text matches any of the HD_VALUES then setting it to "Y" makes the HD symbol appear in Zap2It
    # program description object
    desc = ""
    p_desc = program.findall("desc")
    if len(p_desc) > 0:
        for d in p_desc: # so, i think at some point i'm going to make a configurable preferred language, at which point i'll target that here.
            desc = d.text # just collect the first description for now 
            break # exit the loop
    
    unk_A = "" # TBD
    unk_B = "" # TBD
    unk_C = "" # TBD
    unk_D = "" # TBD

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

    return DEL # return our delimited string

def get_station_name(display_names:list):
    '''Returns the best available display name as a string from a provided list of <display-name> tags.'''
    names = []
    for item in display_names:
        if isinstance(item.text, str):
            text = item.text.strip() if hasattr(item, "text") else str(item).strip()
            if text:
                names.append(text)
    if not names: # there were no names to parse...?
        return "ERROR" # return default string
    
    def score(name):
        upper = name.upper()
        starts_with_call = upper.startswith(("W", "K")) # we prefer display names repesenting a call sign, which can either begin with K or W in the USA
        preferred_len = 3 <= len(name) <= 6 # 3 to 6 letters is perfect, as zap2it can only display 6 letters anyway
        return (
            starts_with_call, # true if K or W
            preferred_len, # true if within length bounds
            -abs(len(name) - 4), # closer to 4 chars is better
            -len(name), # shorter is better
        )
    best_name = max(names, key=score) # get the best name by scoring each one
    if len(best_name) > 6: best_name = best_name[:6] # forcefully limit to 6 chars if we couldnt derive a better name
    return best_name
    

def XMLTV2DEL(xmltv:str, target_channel_id:str, channel_info:dict) -> list: # DEL? ...like Delamain?
    # digest string to actual XML
    tree = ET.fromstring(xmltv)
    # get the target channel id from the channels list, if not provided
    channels = tree.findall("channel")
    channel = None
    if not target_channel_id:
        # get the first channel id in the list
        target_channel_id = channels[0].attrib.get("id", None)
        if not target_channel_id:
            log.error(f"No channel ID could be derived.")
            return []
        
    # collect details about the channel itself, specifically call letters
    for c in channels:
        if c.attrib.get("id", None) == target_channel_id:
            c_names = c.findall("display-name")
            channel_name = get_station_name(c_names) # get the best name
            channel_info["ch_letters"] = channel_name # append our channel callsign to our channel information dict
            log.debug(f"Found channel '{target_channel_id}' ({channel_name}) in XMLTV data.")
            break # no need to continue, ignores any dupes

    # now process programs
    PROGRAMS_DEL = []
    programs = tree.findall("programme")
    programs_for_this_channel = 0
    channel_num = channel_info.get("ch_num")
    for program in programs:
        if program.attrib.get("channel") == target_channel_id:
            programs_for_this_channel += 1 # keep track of how many programs are actually available for this channel id
            DEL_prog = conv_program(program, channel_info=channel_info)
            PROGRAMS_DEL.append(DEL_prog)
    log.info(f"Converted {len(PROGRAMS_DEL)}/{programs_for_this_channel} programs to OnCable delimited format for channel ID '{target_channel_id}' ({channel_num})") # show amount successfully converted
    #log.debug(PROGRAMS_DEL)
    return PROGRAMS_DEL
import logging
log = logging.getLogger(__name__)
import os, requests, pytz
from datetime import datetime as DT
from common import get_config

PROGRAM_DIR = os.path.dirname(os.path.abspath(__file__)) 

def export(text:str, filepath:str):
    if text:
        with open(filepath, "w") as f:
            f.write(text)
            f.close()
            log.debug(f"Wrote {filepath}")

def get_weather_data(cfg:dict):
    '''Collect all weather data (current and forecast) for a given config in a single request.'''
    api_key = cfg.get("weatherapi.com-api-key", None) # gotta have that thang
    headend_id = cfg.get("headend", "ZAP2IT") # default headend ID in the IA release of Zap2It is "ZAP2IT"
    location = cfg.get("locname", "Place 2") # location name...
    zipcode = cfg.get("zipcode", 60601)
    icon_map = get_config('wxcodemap') # our WeatherAPI -> AccuWeather/Zap2It codes
    data = None
    try:
        if api_key:
            request_url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={zipcode}&aqi=no&days=3&alerts=no" # current & forecast data, one request
            r = requests.get(request_url)
            r.raise_for_status()
            data = r.json()
    except:
        log.error(f"Failure during collection of weather data.", exc_info=True)
    if data: # continue processing if valid data 
        timezone_str = data.get("location", {}).get("tz_id", "Etc/Utc") # derive timezone from API, default to UTC if bad timezone string
        timezone = pytz.timezone(timezone_str) 
        # PART 1: CURRENT CONDITIONS
        data_cc = data.get("current", {})
        temperature = round(data_cc.get("temp_f", (data_cc.get("temp_c", -999) * 9/5) + 32)) # fallback to celsius if user doesn't enable temp_f on their api response fields
        condition = data_cc.get("condition", {}).get("text", "Unavailable")
        icon = str(data_cc.get("condition", {}).get("code", "0")) # enforce to string, our map is in strings
        state = "day" if data_cc.get("is_day", 1) == 1 else "night"
        icon_code = icon_map.get(icon, {}).get(state, "")
        wind_dir = data_cc.get("wind_dir", "")
        altimeter = data_cc.get("pressure_in", "")
        unk_A = ""
        unk_B = ""
        unk_C = ""
        unk_D = ""
        #"ZAP2IT|Chicago|56|CLEAR|NNW|1|77|30.33|10|58|"
        # potential format:
        # headend | location name | temperature | condition text | wind direction | unknown A | unknown B | altimeter | unknown C | unknown D |
        # not entirely sure what the unknowns are, but Frix and I haven't been able to get the current conditions to even show up on zap2it so if you figure this out pls fork and PR
        output_cc = f"{headend_id}|{location}|{temperature}|{condition.upper()}|{wind_dir}|{unk_A}|{unk_B}|{altimeter}|{unk_C}|{unk_D}|"
        # PART 2: 3-DAY FORECAST
        # notice: some of the following code is reused from the former weather script, so if you notice inconsistencies, i apologize!!
        fcstdatadays = data.get("forecast", {}).get("forecastday", [])
        output_3d = f"{headend_id}|{location}|"
        if len(fcstdatadays) > 0:
            for i in range(3):
                try:
                    fcstdata = fcstdatadays[i]
                    ts = fcstdata.get("date_epoch", 0)
                    fcst_dt = DT.fromtimestamp(ts, tz=pytz.UTC) # WeatherAPI delivers in UTC
                    day = fcst_dt.strftime("%a") # get the name as a shortened string (this has a map inside of Zap2It's AccuWeather Setup)
                    high = fcstdata.get("day", {}).get("maxtemp_f", 999)
                    low = fcstdata.get("day", {}).get("mintemp_f", -999)
                    ico = str(fcstdata.get("day", {}).get("condition", {}).get("code", "0"))
                    if isinstance(high, float): high = int(round(high))
                    if isinstance(low, float): low = int(round(low))
                    icon = icon_map.get(ico, {}).get("day", "00")
                    output_3d += f"{day}|{high}|{low}|{icon}|"
                except:
                    log.error(f"Error occurred trying to process forecast data.", exc_info=True)
        # PART 3: 18-HOUR FORECAST
        output_18 = f"{headend_id}|{location}|"
        start_targets = [0, 6, 12, 18]
        daypart_codes = {
            0: {"abr": "NITE", "full": "Night"},
            6: {"abr": "MOR", "full": "Morning"},
            12: {"abr": "AFT", "full": "Afternoon"},
            18: {"abr": "EVE", "full": "Evening"}
        }
        current_hour = DT.now(tz=timezone).hour # get the current our derived from the location's timezone
        start_hour = next((num for num in start_targets if num > current_hour), 24) # find the closest available future hour
        if start_hour == 24:
            day = 1 # skip to the next day's forecast data
        else:
            day = 0
        if len(fcstdatadays) > 0:
            data_hour = start_hour % 24 # wrap after 24 hours
            for i in range(3):
                fcstdata = fcstdatadays[day] # get our forecast day
                fcstdatahours = fcstdata.get("hour", []) # should be 24 items i think
                fcstdata = fcstdatahours[data_hour]
                # okay this is gonna be a little weird because there's no hi/low temp on the hourly forecast
                # we'll use the feels like temperature as the "high" and then the forecasted temperature as the low
                # this won't come back to bite me, no....
                daypart = daypart_codes.get(data_hour, {}).get("abr", "WHA")
                daypartname = daypart_codes.get(data_hour, {}).get("full", "What")
                high = fcstdata.get("feelslike_f", 999)
                low = fcstdata.get("temp_f", -999)
                ico = fcstdata.get("condition", {}).get("code", 0)
                ico = str(ico)
                if isinstance(high, float): high = int(round(high))
                if isinstance(low, float): low = int(round(low))
                icon = icon_map.get(ico, {}).get("day", "00")

                output_18 += f"{daypart}|{daypartname}|{high}|{low}|{icon}|"
                # progression by 6 hours for next daypart
                data_hour += 6
                if data_hour >= len(fcstdatahours): # should always be compared to 24
                    day += 1 # progress to next day
                    data_hour = 0
                # that oughta do it
            # FINALE: EXPORT IT.
            export_cfg = get_config('export')
            export_dir = export_cfg.get("dir")
            export(output_cc, os.path.join(export_dir, "uscur.txt")) # export CC
            export(output_3d, os.path.join(export_dir, "us3day.txt")) # export 3 day
            export(output_18, os.path.join(export_dir, "18hour.txt")) # export 18 hour
            log.info(f"Collected and exported all weather data for {location} ({zipcode})!")

if __name__ == "__main__":
    import coloredlogs
    coloredlogs.install(level="DEBUG")
    cfg = get_config("weather")
    get_weather_data(cfg)